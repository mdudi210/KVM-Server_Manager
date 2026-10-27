import os

from dotenv import load_dotenv
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

load_dotenv()


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


AUTHJWT_SECRET_KEY = os.getenv("AUTHJWT_SECRET_KEY")
if not AUTHJWT_SECRET_KEY:
    raise RuntimeError("AUTHJWT_SECRET_KEY must be set")


class Settings(BaseModel):
    authjwt_secret_key: str = AUTHJWT_SECRET_KEY
    authjwt_token_location: set = {"headers", "cookies"}
    authjwt_cookie_secure: bool = _as_bool(os.getenv("AUTHJWT_COOKIE_SECURE"), False)
    authjwt_cookie_samesite: str = os.getenv("AUTHJWT_COOKIE_SAMESITE", "lax")
    authjwt_cookie_csrf_protect: bool = _as_bool(os.getenv("AUTHJWT_COOKIE_CSRF_PROTECT"), False)
    authjwt_access_cookie_key: str = os.getenv("AUTHJWT_ACCESS_COOKIE_KEY", "access_token_cookie")


settings = Settings()


@AuthJWT.load_config
def get_config():
    return settings
