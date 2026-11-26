"""User routes: list, get, update, delete users."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from authapi.database import get_db
from authapi.deps import CurrentSuperUser, CurrentUser
from authapi.models import User
from authapi.schemas import Message, UserRead, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_user_me(current_user: CurrentUser) -> UserRead:
    """Get the current authenticated user."""
    return current_user


@router.get("", response_model=list[UserRead])
async def read_users(
    current_user: CurrentSuperUser,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> list[UserRead]:
    """List all users (superuser only)."""
    from sqlalchemy import select

    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users  # type: ignore[return-value]


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    current_user: CurrentSuperUser,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Get a user by ID (superuser only)."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    current_user: CurrentSuperUser,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Update a user (superuser only)."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: int,
    current_user: CurrentSuperUser,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """Delete a user (superuser only)."""
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return Message(detail="User deleted successfully")
