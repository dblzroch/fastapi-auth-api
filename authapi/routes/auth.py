"""Authentication routes: login, register, refresh, password reset."""

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from authapi.auth import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_reset_token,
    revoke_refresh_token,
    store_refresh_token,
    store_reset_token,
)
from authapi.database import get_db
from authapi.deps import get_current_active_user
from authapi.models import RefreshToken, User
from authapi.schemas import (
    Message,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    TokenRefresh,
    UserCreate,
    UserRead,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    """Register a new user."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/token", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Log in and receive access + refresh tokens."""
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.username)
    refresh_token = create_refresh_token(subject=user.username)
    await store_refresh_token(db, user, refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(token_in: TokenRefresh, db: AsyncSession = Depends(get_db)) -> Token:
    """Refresh an access token using a refresh token."""
    from sqlalchemy import select

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == token_in.refresh_token)
    )
    rt = result.scalar_one_or_none()
    if not rt or rt.revoked:
        raise HTTPException(status_code=401, detail="Invalid or revoked refresh token")

    result = await db.execute(select(User).where(User.id == rt.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token(subject=user.username)
    new_refresh_token = create_refresh_token(subject=user.username)
    await revoke_refresh_token(db, token_in.refresh_token)
    await store_refresh_token(db, user, new_refresh_token)
    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout", response_model=Message)
async def logout(
    token_in: TokenRefresh,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Message:
    """Revoke a refresh token (logout)."""
    await revoke_refresh_token(db, token_in.refresh_token)
    return Message(detail="Logged out successfully")


@router.post("/password-reset/request", response_model=Message)
async def password_reset_request(
    reset_in: PasswordResetRequest, db: AsyncSession = Depends(get_db)
) -> Message:
    """Request a password reset token."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.email == reset_in.email))
    user = result.scalar_one_or_none()
    if not user:
        return Message(detail="If the email exists, a reset link was sent")
    reset_token = create_refresh_token(subject=user.username)
    await store_reset_token(db, user, reset_token)
    return Message(detail="Reset token generated")


@router.post("/password-reset/confirm", response_model=Message)
async def password_reset_confirm(
    reset_in: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
) -> Message:
    """Confirm a password reset with a token."""
    reset_token = await get_reset_token(db, reset_in.token)
    if not reset_token or reset_token.used:
        raise HTTPException(status_code=status.HTTP_400, detail="Invalid or used token")

    from datetime import UTC, datetime

    from sqlalchemy import select

    if reset_token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=400, detail="Token expired")

    result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.hashed_password = get_password_hash(reset_in.new_password)
    reset_token.used = True
    await db.commit()
    return Message(detail="Password reset successfully")
