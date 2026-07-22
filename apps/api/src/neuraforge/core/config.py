from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-validated configuration (SRS §10.1: .env + Pydantic Settings)."""

    model_config = SettingsConfigDict(env_prefix="NF_", env_file=".env", extra="ignore")

    env: Literal["dev", "staging", "production"] = "dev"
    database_url: str = "sqlite+aiosqlite:///./neuraforge-dev.db"
    cors_origins: list[str] = ["http://localhost:3000"]
    api_prefix: str = "/api/v1"
    auto_seed: bool = True  # dev convenience; ignored outside dev

    # ── auth (ADR-0007) ──
    access_token_ttl_s: int = 15 * 60
    refresh_token_ttl_s: int = 30 * 24 * 3600
    verify_token_ttl_s: int = 24 * 3600
    jwt_key_file: str = ".dev-keys/jwt-ed25519.pem"  # prod: systemd LoadCredential path
    # Dev ergonomics: unauthenticated requests fall back to the seeded demo
    # user so the learning UI works before the web app ships full token plumbing.
    # MUST be false outside dev; enforced in config validation below.
    dev_autologin: bool = True

    # ── Ember AI tutor (FR-TUTOR-*, ARCHITECTURE.md §10) ──
    ember_enabled: bool = True
    ember_base_url: str = "http://localhost:11434/v1"  # any OpenAI-compatible endpoint
    ember_model: str = "llama3.2"
    ember_api_key: str = ""  # empty for local Ollama
    ember_timeout_s: float = 60.0
    ember_daily_token_budget: int = 50_000  # per learner (FR-TUTOR-8)

    # ── Assessment engine (FR-ASSESS-*, SRS §9) ──
    # Lightweight subprocess sandbox (Phase 11 scope decision); the OS-level
    # hardening in SRS §9 (systemd-run, seccomp, cgroups) is Phase 12 (Linux-
    # only prod deployment), not reproducible on this dev host.
    assess_submission_wall_s: float = 10.0
    assess_submission_mem_mb: int = 256
    assess_submission_output_cap: int = 4000
    assess_max_attempts_per_exercise: int = 20

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"

    def model_post_init(self, __context: object) -> None:
        if self.env != "dev" and self.dev_autologin:
            raise ValueError("NF_DEV_AUTOLOGIN must be false outside dev")


@lru_cache
def get_settings() -> Settings:
    return Settings()
