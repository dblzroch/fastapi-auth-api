"""Authentication utilities: password hashing, JWT tokens."""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt  # type: ignore[import-untyped]
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .models import RefreshToken, ResetToken, User


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"sub": str(subject), "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt  # type: ignore[no-any-return]


def create_refresh_token(subject: str | Any) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": str(subject), "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt  # type: ignore[no-any-return]


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload  # type: ignore[no-any-return]
    except JWTError:
        return None


async def store_refresh_token(db: AsyncSession, user: User, token: str) -> None:
    """Store a refresh token in the database."""
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(token=token, user_id=user.id, expires_at=expires_at))
    await db.commit()


async def store_reset_token(db: AsyncSession, user: User, token: str) -> None:
    """Store a password reset token in the database."""
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
    )
    db.add(ResetToken(token=token, user_id=user.id, expires_at=expires_at))
    await db.commit()


async def revoke_refresh_token(db: AsyncSession, token: str) -> None:
    """Revoke a refresh token."""
    from sqlalchemy import select

    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
    rt = result.scalar_one_or_none()
    if rt:
        rt.revoked = True
        await db.commit()


async def is_refresh_token_revoked(db: AsyncSession, token: str) -> bool:
    """Check if a refresh token is revoked."""
    from sqlalchemy import select

    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
    rt = result.scalar_one_or_none()
    return rt is not None and rt.revoked


async def get_reset_token(db: AsyncSession, token: str) -> ResetToken | None:
    """Get a reset token by value."""
    from sqlalchemy import select

    result = await db.execute(select(ResetToken).where(ResetToken.token == token))
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    """Authenticate a user by username and password."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
