from datetime import datetime, timedelta, timezone
import os
import jwt  # PyJWT
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session_sql import get_db
from app.repositories.market_repository import MarketRepository
from app.schemas.auth import GetUserRequest  # we won't enforce LoginResponse so we can include both casings

# ----------------- config helpers -----------------
def _get_auth_config():
    # Match .NET keys; allow env fallbacks
    jwt_secret = (
        os.getenv("Authentication__JwtSecret")
        or os.getenv("AUTHENTICATION_JWTSECRET")
        or os.getenv("JWT_SECRET")
    )
    issuer = (
        os.getenv("Authentication__Issuer")
        or os.getenv("AUTHENTICATION_ISSUER")
        or os.getenv("JWT_ISSUER")
        or "PyCreativeHandsApi"
    )
    audience = (
        os.getenv("Authentication__Audience")
        or os.getenv("AUTHENTICATION_AUDIENCE")
        or os.getenv("JWT_AUDIENCE")
        or "CreativeHandsClients"
    )
    if not jwt_secret:
        raise RuntimeError("Authentication:JwtSecret is not configured")
    return jwt_secret, issuer, audience

def _generate_jwt(username: str, is_admin: bool) -> str:
    secret, issuer, audience = _get_auth_config()
    now = datetime.now(tz=timezone.utc)
    payload = {
        "name": username,                         # ClaimTypes.Name
        "role": "Admin" if is_admin else "User",  # ClaimTypes.Role
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=12)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")

# ----------------- dependency -----------------
def get_repo(db: Session = Depends(get_db)) -> MarketRepository:
    return MarketRepository(db)

# ----------------- base router -----------------
_base = APIRouter(tags=["Auth"])

@_base.post("/login")
async def login(request: GetUserRequest, repo: MarketRepository = Depends(get_repo)):
    users = await run_in_threadpool(repo.get_users, request)
    user = users[0] if users else None
    if not user:
        # exactly like .NET
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    token = _generate_jwt(user.UserName, bool(user.IsAdmin))

    # Build BOTH payload shapes:
    pascal_user = {
        "Id": user.Id,
        "UserName": user.UserName,
        "FullName": user.FullName,
        "IsAdmin": bool(user.IsAdmin),
    }
    camel_user = {
        "id": user.Id,
        "userName": user.UserName,
        "fullName": user.FullName,
        "isAdmin": bool(user.IsAdmin),
    }

    # Return both casings so legacy .NET clients and JS clients are happy
    return JSONResponse({
        "Token": token,          # PascalCase (matches .NET)
        "User": pascal_user,
        "token": token,          # camelCase (what many JS clients expect)
        "user": camel_user,
    })

# ----------------- exported router (both cases) -----------------
router = APIRouter()
router.include_router(_base, prefix="/auth", tags=["Auth"])
router.include_router(_base, prefix="/Auth", tags=["Auth"])
