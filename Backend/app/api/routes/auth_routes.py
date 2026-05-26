import hashlib, jwt, time
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Response, status
from app.api.db.client import db
from app.models.api_schemas import LoginRequest, SignupRequest
import os
from app.core.config import (
    JWT_COOKIE_NAME,
    JWT_EXPIRATION_SECONDS,
    JWT_SECRET_KEY
)


router = APIRouter(prefix="/auth", tags=["auth"])
users_collection = db["users"]



def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def _create_jwt(id: str, email: str) -> str:
    issued_at = int(time.time())
    return jwt.encode(
        {
            "id": id,
            "email":email,
            "iat": issued_at,
            "exp":issued_at + int(JWT_EXPIRATION_SECONDS)
        },
        JWT_SECRET_KEY,
        algorithm="HS256"
    )


@router.post("/signup")
def signup(payload: SignupRequest):
    email = payload.email.strip().lower()
    name = payload.name.strip()

    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    user_id = str(uuid4())
    
    user_document = {
        "id": user_id,
        "name": name,
        "email": email,
        "password_hash": _hash_password(payload.password),
        "created_at": datetime.utcnow()
    }

    users_collection.insert_one(user_document)

    return {
        "success": True,
        "message": "Signup successful",
        "user": {
            "id": user_id,
            "name": name,
            "email": email
        }
    }


@router.post("/login")
def login(payload: LoginRequest, response: Response):
    email = payload.email.strip().lower()
    user = users_collection.find_one({"email": email})

    if not user or user.get("password_hash") != _hash_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = _create_jwt(user["id"], user["email"])

    response.set_cookie(
        key=JWT_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=os.getenv("ENVIRONMENT") == "production", #changes here
        samesite="lax",
        max_age=JWT_EXPIRATION_SECONDS,
        path="/"
    )

    return {
        "success": True,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }