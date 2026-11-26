# fastapi-auth-api

Reusable authentication service with JWT, refresh tokens, RBAC, and password recovery.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-d7314f.svg)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.13-5c4a4e.svg)](https://alembic.sqlalchemy.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy strict](https://img.shields.io/badge/mypy-strict-blue.svg)](http://mypy.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- User registration with email and username uniqueness
- JWT access + refresh token authentication (password reset included)
- Password hashing with bcrypt
- Role-based access (superuser endpoints)
- Async SQLAlchemy 2.0 + Alembic migrations
- Pydantic v2 schemas
- 100% typed, mypy strict, ruff lint + format
- pytest with coverage gate

## Quickstart

```bash
# Clone
git clone https://github.com/dblzroch/fastapi-auth-api.git
cd fastapi-auth-api

# Install deps
uv sync --dev

# Copy env example
cp .env.example .env
# Edit .env with your own SECRET_KEY

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn authapi.main:app --reload

# Run tests
uv run pytest
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register a new user | None |
| POST | `/api/v1/auth/token` | Login (access + refresh tokens) | None |
| POST | `/api/v1/auth/refresh` | Refresh access token | None |
| POST | `/api/v1/auth/logout` | Revoke refresh token | Bearer |
| POST | `/api/v1/auth/password-reset/request` | Request password reset | None |
| POST | `/api/v1/auth/password-reset/confirm` | Confirm password reset | None |
| GET | `/api/v1/users/me` | Get current user | Bearer |
| GET | `/api/v1/users` | List users | Superuser |
| GET | `/api/v1/users/{id}` | Get user by ID | Superuser |
| PATCH | `/api/v1/users/{id}` | Update user | Superuser |
| DELETE | `/api/v1/users/{id}` | Delete user | Superuser |

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLAlchemy 2.0 (async) + Alembic
- **Auth:** JWT (python-jose), bcrypt
- **Validation:** Pydantic v2
- **Testing:** pytest, httpx, coverage
- **Lint/Format:** ruff
- **Types:** mypy strict

## Project Standards

- Python 3.12+
- `uv` with `[dependency-groups]` (PEP 735)
- `ruff check` + `ruff format`
- `mypy strict`
- `pytest` with coverage ≥ 60%
- CI on GitHub Actions
- `.env.example` committed, never `.env`
- Conventional Commits
- README in English
- MIT License, 2026, Diego (dblzroch)

## License

MIT License — see [LICENSE](LICENSE).
