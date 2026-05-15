import base64
import hashlib
import hmac
import secrets
from time import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import AUTH_SECRET
from app.services import storage


TOKEN_TTL_SECONDS = 60 * 60 * 24
security = HTTPBearer(auto_error=False)


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return digest.hex(), salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    candidate, _ = hash_password(password, salt)
    return hmac.compare_digest(candidate, password_hash)


def create_token(user_id: int, username: str) -> str:
    expires = int(time()) + TOKEN_TTL_SECONDS
    payload = f"{user_id}:{username}:{expires}"
    signature = hmac.new(AUTH_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    token = f"{payload}:{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(token).decode("utf-8")


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    try:
        decoded = base64.urlsafe_b64decode(credentials.credentials.encode("utf-8")).decode("utf-8")
        user_id_text, username, expires_text, signature = decoded.rsplit(":", 3)
        payload = f"{user_id_text}:{username}:{expires_text}"
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.") from exc

    expected = hmac.new(AUTH_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected) or int(expires_text) < int(time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

    user = storage.get_user_by_id(int(user_id_text))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")
    return user
