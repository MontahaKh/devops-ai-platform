"""Security utilities for authentication."""
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import UserRole
from app.database import get_db
from app.models.user import User

password_hasher = PasswordHash.recommended()
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash a password."""
    return password_hasher.hash(password)


def create_access_token(subject: str, username: str) -> str:
    """Create a JWT access token."""
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "username": username,
        "exp": now + expires_delta,
        "iat": now,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, username: str) -> str:
    """Create a JWT refresh token."""
    expires_delta = timedelta(days=7)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "username": username,
        "exp": now + expires_delta,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get the current authenticated user."""
    payload = decode_token(credentials.credentials)
    subject = payload.get("sub")
    jti = payload.get("jti")
    
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if token is blacklisted
    if jti and is_token_blacklisted(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def add_token_to_blacklist(db: Session, token: str, user_id: int) -> None:
    """Add a token to the blacklist."""
    from app.models import TokenBlacklist

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not jti or not exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if is_token_blacklisted(db, jti):
        return

    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    blacklisted_token = TokenBlacklist(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(blacklisted_token)
    db.commit()


def is_token_blacklisted(db: Session, jti: str) -> bool:
    """Check if a token is blacklisted."""
    from app.models import TokenBlacklist

    token = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
    return token is not None


def ensure_token_not_blacklisted(db: Session, payload: dict) -> None:
    """Reject a token that was already revoked."""
    jti = payload.get("jti")
    if not jti or is_token_blacklisted(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*roles: UserRole):
    """Dependency to require specific user roles."""
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [r.value for r in roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {', '.join([r.value for r in roles])}",
            )
        return current_user

    return check_role
