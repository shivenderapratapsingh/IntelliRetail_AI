from fastapi import Request
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import (
    JWT_COOKIE_NAME,
    JWT_SECRET_KEY
)

ALGORITHM = "HS256"


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        public_routes = [
            "/",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/auth/login",
            "/auth/signup"
        ]

        # Skip public routes
        if request.url.path in public_routes:
            return await call_next(request)

        # Get token from cookie
        token = request.cookies.get(JWT_COOKIE_NAME)

        if not token:
            return JSONResponse(
                status_code=401,
                content={
                    "message": "Authentication required"
                }
            )

        try:

            payload = jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            request.state.user = payload

        except JWTError:

            return JSONResponse(
                status_code=401,
                content={
                    "message": "Invalid or expired token"
                }
            )

        return await call_next(request)