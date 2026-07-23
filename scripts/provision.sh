#!/usr/bin/env bash
# Idempotent server bootstrap (SRS §10.4). Run once per server, and safely
# re-runnable after — every step checks current state before acting.
#
#   sudo bash scripts/provision.sh
#
# Docker-free by design (ADR-0002): packages, users, and directories only —
# no container runtime anywhere in this pipeline.
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash scripts/provision.sh" >&2
  exit 1
fi

NF_ROOT=/opt/neuraforge
NF_CONF=/etc/neuraforge

echo "==> Installing system packages"
apt-get update -qq
apt-get install -y -qq nginx postgresql postgresql-contrib ufw fail2ban unattended-upgrades curl openssh-server

echo "==> Creating service users"
for user in nf-api nf-web; do
  if ! id "$user" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin "$user"
    echo "    created $user"
  else
    echo "    $user already exists"
  fi
done

echo "==> Creating directories"
install -d -o root -g root -m 755 "$NF_ROOT" "$NF_ROOT/releases"
install -d -o root -g root -m 750 "$NF_CONF"

echo "==> Installing uv (Python toolchain, ADR-0003) and Node 20 LTS (build-time only)"
if [[ ! -x "$NF_ROOT/tools/uv/uv" ]]; then
  install -d "$NF_ROOT/tools/uv"
  curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR="$NF_ROOT/tools/uv" sh
fi
if [[ ! -x "$NF_ROOT/node/bin/node" ]]; then
  install -d "$NF_ROOT/node"
  curl -fsSL https://nodejs.org/dist/v20.18.1/node-v20.18.1-linux-x64.tar.xz \
    | tar -xJ -C "$NF_ROOT/node" --strip-components=1
fi

echo "==> Provisioning PostgreSQL role + database"
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='neuraforge'" | grep -q 1; then
  read -rsp "    Set a password for the 'neuraforge' DB role: " NF_DB_PASSWORD
  echo
  sudo -u postgres psql -c "CREATE ROLE neuraforge WITH LOGIN PASSWORD '${NF_DB_PASSWORD}';"
else
  echo "    role 'neuraforge' already exists"
fi
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='neuraforge'" | grep -q 1; then
  sudo -u postgres psql -c "CREATE DATABASE neuraforge OWNER neuraforge;"
else
  echo "    database 'neuraforge' already exists"
fi

echo "==> Generating JWT signing key (EdDSA/Ed25519, ADR-0007)"
if [[ ! -f "$NF_CONF/jwt-ed25519.pem" ]]; then
  python3 - "$NF_CONF/jwt-ed25519.pem" <<'PYEOF'
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

key = Ed25519PrivateKey.generate()
pem = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
with open(sys.argv[1], "wb") as f:
    f.write(pem)
PYEOF
  chown root:root "$NF_CONF/jwt-ed25519.pem"
  chmod 600 "$NF_CONF/jwt-ed25519.pem"
  echo "    generated $NF_CONF/jwt-ed25519.pem"
else
  echo "    JWT key already present — leaving it alone (rotating it invalidates all sessions)"
fi

echo "==> Environment files"
if [[ ! -f "$NF_CONF/api.env" ]]; then
  echo "    WARNING: $NF_CONF/api.env missing — copy apps/api/.env.prod.example there and fill it in before starting neuraforge-api"
fi

echo "==> systemd units"
cp deploy/systemd/neuraforge-api.service deploy/systemd/neuraforge-web.service /etc/systemd/system/
systemctl daemon-reload

echo "==> Nginx"
cp deploy/nginx/neuraforge.conf /etc/nginx/sites-available/neuraforge.conf
ln -sf /etc/nginx/sites-available/neuraforge.conf /etc/nginx/sites-enabled/neuraforge.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo "==> Firewall"
ufw allow OpenSSH >/dev/null
ufw allow 'Nginx Full' >/dev/null
ufw --force enable >/dev/null

echo "==> Enabling services"
systemctl enable --now postgresql nginx fail2ban unattended-upgrades
# `enable --now` is a no-op on an already-running nginx — it would otherwise
# keep serving whatever config was in memory when it first started, silently
# ignoring the file just copied above (caught live-testing this script: the
# API route 404'd through Nginx while working fine directly, because Nginx
# had never actually reloaded).
systemctl reload nginx

cat <<'EOF'

Provisioning complete. Before the first deploy:
  1. Fill in /etc/neuraforge/api.env (from apps/api/.env.prod.example) with
     the real DB password set above and your domain in NF_CORS_ORIGINS.
  2. Point DNS at this server and run: certbot --nginx -d your-domain.example
  3. Run scripts/deploy.sh <path-to-checked-out-release>
EOF
