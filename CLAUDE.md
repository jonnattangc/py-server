# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal experimental Flask REST API server (`dev.jonnattan.com`) hosting 33+ services covering diverse integrations: AWS (Pinpoint, S3), OAuth/CAPTCHA, WhatsApp via Waza, Atlassian (Confluence/Jira), LLM/ML endpoints, geolocation, email, cryptography, and more.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server (port argument required)
python app/http-server.py 8085

# Run tests with coverage
pytest

# Run a single test file
pytest tests/unit/test_factory.py -v

# Docker (requires sibling ../envs/ directory with file.env and file.aws_credentials)
docker-compose up
```

## Architecture

Layered architecture with an evolving migration from a legacy monolith:

- **API Layer** (`app/api/routes/`) — Flask blueprints, one per service domain (check, crypto, mail, waza, ucc, logia, cxp, zlr, edr, dreams, page, status, main)
- **Application Layer** (`app/application/`) — Reserved for use-case services (mostly empty)
- **Domain Layer** (`app/domain/`) — Interfaces/ports (`IUserRepository`, `IOtpRepository`, `IDatabaseConnection`) and entity definitions
- **Infrastructure Layer** (`app/infrastructure/`) — Concrete MySQL repositories (`mysql_repositories.py`), HTTP Basic Auth (`basic_auth.py`)
- **Legacy Layer** (`app/legacy/`) — 23 original business-logic modules still in use; blueprints delegate to these while migration progresses

**App factory:** `app/__init__.py` → `create_app()` registers blueprints, initializes extensions (CSRF, CORS, HTTPBasicAuth), and configures Swagger/Flasgger. Blueprint registration happens in `app/api/__init__.py` → `register_blueprints()`.

**Config:** `app/config.py` — single `Config` class reading all env vars. No `.env` file; secrets are provided via `../envs/file.env` in Docker or set in the shell for local runs.

**Database:** PyMySQL, new connection per request (no pooling). Env vars: `HOST_BD`, `PORT_BD`, `USER_BD`, `PASS_BD`, `SCHEMA_BD`.

**Auth:** HTTP Basic Auth via `BasicAuthProvider` backed by `UserRepository` (MySQL). The `/checkall` endpoint is the main auth-protected route.

**Swagger docs:** Available at `/apidocs/` — auto-generated from route docstrings + Flasgger config in `create_app()`.

## Testing

- Config in `pytest.ini`; test path is `tests/unit/`, coverage enforced at ≥60%
- `conftest.py` provides: `app` fixture (CSRF disabled, testing mode), `client`, `runner`, `mock_pymysql`, and an auto-patched `patch_auth` that bypasses real DB lookups
- Legacy module tests use heavy mocking of external deps (`boto3`, `requests`, `pymysql`, `imaplib`)

## Docker Quirks

- `.dockerignore` excludes everything except `requirements.txt` — the image has no app code
- App code is **volume-mounted** at runtime from `./app`
- Requires `../envs/file.env` and `../envs/file.aws_credentials` in a sibling directory (not versioned)

## CI/CD

GitHub Actions run on push/PR to `main` and `develop`:
- `docker-image.yml` — builds the Docker image
- `sonarqube.yml` — SonarCloud analysis (also triggers on `feature/re-organizacion`)
- `codeql.yml` — CodeQL security scan (also weekly schedule)

No automated test execution in CI.
