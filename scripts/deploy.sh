#!/usr/bin/env bash
# Release deploy (SRS §10.4): copy a checked-out source tree into a new
# releases/<timestamp>/ directory, build it in place, migrate the database,
# atomically flip the `current` symlink, restart services, and roll back
# automatically if the post-deploy health check fails.
#
#   sudo bash scripts/deploy.sh /path/to/checked-out/source
#
# The source is any directory containing the repo at the ref you want to
# ship — a git worktree at a tag, or a CI checkout. This script does not
# take a git ref itself; checking out the right commit is the caller's job
# (see .github/workflows/release.yml for the CI-driven version of that).
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash scripts/deploy.sh <source-dir>" >&2
  exit 1
fi

SRC="${1:?Usage: deploy.sh <source-checkout-dir>}"
NF_ROOT=/opt/neuraforge
NF_CONF=/etc/neuraforge
RELEASE_ID=$(date +%Y%m%d%H%M%S)
RELEASE_DIR="$NF_ROOT/releases/$RELEASE_ID"
CURRENT="$NF_ROOT/current"
export PATH="$NF_ROOT/tools/uv:$NF_ROOT/node/bin:$PATH"

log() { echo "==> $*"; }

if [[ ! -f "$NF_CONF/api.env" ]]; then
  echo "Missing $NF_CONF/api.env — run scripts/provision.sh first and fill it in." >&2
  exit 1
fi

log "Copying $SRC -> $RELEASE_DIR"
install -d "$RELEASE_DIR"
rsync -a \
  --exclude='.git' --exclude='node_modules' --exclude='.venv' \
  --exclude='__pycache__' --exclude='*.db' --exclude='.next' \
  "$SRC"/ "$RELEASE_DIR"/

log "Building API (uv sync --frozen)"
(cd "$RELEASE_DIR/apps/api" && uv sync --frozen)

log "Running database migration (alembic upgrade head)"
# Deliberately NOT `source`-ing api.env: bash's quote-removal strips embedded
# quotes anywhere in a word (not just at the start), so
# NF_CORS_ORIGINS=["https://x"] becomes NF_CORS_ORIGINS=[https://x] — valid
# bash, invalid JSON, and pydantic-settings rejects it. `read` captures each
# line as opaque data instead, so quoting inside the value survives intact.
# (The systemd units use `EnvironmentFile=` instead, which never had this bug.)
(
  cd "$RELEASE_DIR/apps/api"
  set -a
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" == \#* ]] && continue
    export "$key=$value"
  done < "$NF_CONF/api.env"
  set +a
  uv run alembic upgrade head
)

log "Building web (npm ci && npm run build)"
(cd "$RELEASE_DIR" && npm ci --no-audit --no-fund && npm run build)

chown -R nf-api:nf-api "$RELEASE_DIR/apps/api"
chown -R nf-web:nf-web "$RELEASE_DIR/apps/web" "$RELEASE_DIR/packages" "$RELEASE_DIR/node_modules"

PREVIOUS=""
if [[ -L "$CURRENT" ]]; then
  PREVIOUS=$(readlink -f "$CURRENT")
fi

log "Switching current -> $RELEASE_DIR"
ln -sfn "$RELEASE_DIR" "$CURRENT"

log "Restarting services"
# `|| true`: a failed restart must fall through to the health check below
# (which will also fail and trigger rollback) rather than let `set -e` kill
# the script here and skip rollback entirely — the exact failure mode
# live-testing this script caught on the first real deploy.
systemctl restart neuraforge-api neuraforge-web || true

log "Health check"
ok=true
curl -sf --max-time 15 http://127.0.0.1:8001/api/v1/health >/dev/null || ok=false
curl -sf --max-time 15 http://127.0.0.1:3000/ >/dev/null || ok=false

if [[ "$ok" == true ]]; then
  log "Deploy OK: $RELEASE_ID"
else
  log "Health check FAILED — rolling back"
  if [[ -n "$PREVIOUS" ]]; then
    ln -sfn "$PREVIOUS" "$CURRENT"
    systemctl restart neuraforge-api neuraforge-web || true
    log "Rolled back to $(basename "$PREVIOUS")"
  else
    log "No previous release to roll back to"
  fi
  exit 1
fi

log "Pruning old releases (keeping last 5)"
# shellcheck disable=SC2012
ls -1dt "$NF_ROOT"/releases/*/ | tail -n +6 | xargs -r rm -rf
