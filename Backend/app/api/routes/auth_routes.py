import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel
from pymongo import MongoClient

from app.core.config import (
    MONGODB_DATABASE,
    MONGODB_URI,
    JWT_COOKIE_NAME,
    JWT_EXPIRATION_SECONDS,
    JWT_SECRET_KEY
)


router = APIRouter(prefix="/auth", tags=["auth"])

client = MongoClient(MONGODB_URI)
database = client[MONGODB_DATABASE]
users_collection = database["users"]

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_EXPIRATION_SECONDS = int(os.getenv("JWT_EXPIRATION_SECONDS"))
JWT_COOKIE_NAME = os.getenv("JWT_COOKIE_NAME")


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _create_jwt(payload: dict[str, object]) -> str:
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    header_b64 = _base64url_encode(
        json.dumps(header, separators=(",", ":")).encode("utf-8")
    )
    payload_b64 = _base64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256
    ).digest()

    return f"{header_b64}.{payload_b64}.{_base64url_encode(signature)}"


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

    issued_at = int(time.time())
    expires_at = issued_at + JWT_EXPIRATION_SECONDS
    token = _create_jwt(
        {
            "sub": user["id"],
            "email": user["email"],
            "name": user["name"],
            "iat": issued_at,
            "exp": expires_at,
            "jti": str(uuid4())
        }
    )

    response.set_cookie(
        key=JWT_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,
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