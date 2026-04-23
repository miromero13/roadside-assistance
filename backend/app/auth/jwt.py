from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

_revoked_token_jti: dict[str, int] = {}


def _utc_ts_now() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _cleanup_revoked_tokens() -> None:
    now_ts = _utc_ts_now()
    expired = [jti for jti, exp_ts in _revoked_token_jti.items() if exp_ts <= now_ts]
    for jti in expired:
        _revoked_token_jti.pop(jti, None)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "jti": str(uuid4())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def revoke_token_payload(payload: dict) -> None:
    _cleanup_revoked_tokens()

    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        return

    try:
        _revoked_token_jti[str(jti)] = int(exp)
    except (TypeError, ValueError):
        return


def is_token_payload_revoked(payload: dict) -> bool:
    _cleanup_revoked_tokens()
    jti = payload.get("jti")
    if not jti:
        return False
    return str(jti) in _revoked_token_jti
