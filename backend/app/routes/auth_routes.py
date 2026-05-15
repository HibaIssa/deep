import sqlite3

from fastapi import APIRouter, HTTPException, status

from app.schemas import AuthResponse, UserCreate, UserLogin
from app.services import storage
from app.services.auth import create_token, hash_password, verify_password


router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register_user(payload: UserCreate):
    username = payload.username.strip().lower()
    if len(username) < 3 or len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters and password at least 6 characters.",
        )

    password_hash, salt = hash_password(payload.password)
    try:
        user_id = storage.create_user(username, password_hash, salt)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.") from exc

    return {"token": create_token(user_id, username), "username": username}


@router.post("/login", response_model=AuthResponse)
def login_user(payload: UserLogin):
    username = payload.username.strip().lower()
    user = storage.get_user_by_username(username)
    if user is None or not verify_password(payload.password, user["password_hash"], user["salt"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    return {"token": create_token(user["id"], user["username"]), "username": user["username"]}
