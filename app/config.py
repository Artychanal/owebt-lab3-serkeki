import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when a required environment variable is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    gemini_api_key: str
    gemini_model: str
    run_mode: str
    webhook_base_url: str | None
    webhook_path: str
    webhook_secret: str | None
    port: int

    @property
    def webhook_url(self) -> str:
        if not self.webhook_base_url:
            raise ConfigError("WEBHOOK_BASE_URL is required in webhook mode")
        return f"{self.webhook_base_url.rstrip('/')}{self.webhook_path}"


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(f"Environment variable {name} is required")
    return value


def load_settings() -> Settings:
    load_dotenv()

    run_mode = os.getenv("RUN_MODE", "polling").strip().lower()
    if run_mode not in {"polling", "webhook"}:
        raise ConfigError("RUN_MODE must be either 'polling' or 'webhook'")

    webhook_path = os.getenv("WEBHOOK_PATH", "/telegram/webhook").strip()
    if not webhook_path.startswith("/"):
        webhook_path = f"/{webhook_path}"

    # Render provides the service URL automatically. Prefer it over a manually
    # configured value so a renamed/recreated service cannot keep a stale URL.
    webhook_base_url = (
        os.getenv("RENDER_EXTERNAL_URL", "").strip()
        or os.getenv("WEBHOOK_BASE_URL", "").strip()
        or None
    )
    webhook_secret = os.getenv("WEBHOOK_SECRET", "").strip() or None

    if run_mode == "webhook":
        if not webhook_base_url:
            raise ConfigError("WEBHOOK_BASE_URL is required in webhook mode")
        if not webhook_base_url.startswith("https://"):
            raise ConfigError("WEBHOOK_BASE_URL must use HTTPS")
        if not webhook_secret:
            raise ConfigError("WEBHOOK_SECRET is required in webhook mode")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,256}", webhook_secret):
            raise ConfigError(
                "WEBHOOK_SECRET may contain only A-Z, a-z, 0-9, '_' and '-'"
            )

    try:
        port = int(os.getenv("PORT", "8080"))
    except ValueError as error:
        raise ConfigError("PORT must be an integer") from error

    return Settings(
        bot_token=_required("TELEGRAM_BOT_TOKEN"),
        gemini_api_key=_required("GEMINI_API_KEY"),
        gemini_model=os.getenv(
            "GEMINI_MODEL", "gemini-3.5-flash-lite"
        ).strip(),
        run_mode=run_mode,
        webhook_base_url=webhook_base_url,
        webhook_path=webhook_path,
        webhook_secret=webhook_secret,
        port=port,
    )
