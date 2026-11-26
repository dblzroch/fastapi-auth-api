"""Tests for fastapi-auth-api authentication service."""

from typing import AsyncGenerator

import pytest
from authapi.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


# ------------------------------------------------------------------
# Register
# ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_register(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "newpass123",
            "full_name": "New User",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["email"] == "newuser@test.com"
    assert data["username"] == "newuser"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "username": "dupuser",
            "password": "pass123",
        },
    )
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@test.com",
            "username": "dupuser2",
            "password": "pass123",
        },
    )
    assert resp.status_code == 400


# ------------------------------------------------------------------
# Login / Token
# ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_login(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@test.com",
            "username": "loginuser",
            "password": "loginpass123",
        },
    )
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "loginuser", "password": "loginpass123"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpw@test.com",
            "username": "wrongpwuser",
            "password": "correctpass123",
        },
    )
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "wrongpwuser", "password": "wrongpass123"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "nonexistent", "password": "whatever"},
    )
    assert resp.status_code == 401


# ------------------------------------------------------------------
# Password reset
# ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_password_reset_request(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "reset@test.com",
            "username": "resetuser",
            "password": "resetpass123",
        },
    )
    resp = await client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "reset@test.com"},
    )
    assert resp.status_code == 200, resp.text


# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ------------------------------------------------------------------
# Unauthenticated access should fail
# ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_me_without_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_users_without_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/users")
    assert resp.status_code == 401


# ------------------------------------------------------------------
# Edge cases
# ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "no@test.com"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.value"},
    )
    assert resp.status_code == 401
