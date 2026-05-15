# AGENTS.md for py-server

## Overview
Personal experimental Flask server (`dev.jonnattan.com`).

The project follows a **layered architecture** with clear separation of concerns:

- **API / Presentation Layer:** Flask blueprints (`app/api/routes/`)
- **Application Layer:** Use-case services (`app/application/`)
- **Domain Layer:** Entities and interfaces/ports (`app/domain/`)
- **Infrastructure Layer:** Concrete implementations (DB, external APIs, auth) (`app/infrastructure/`)
- **Legacy Layer:** Original modules preserved during migration (`app/legacy/`)

## Running Locally
- **Entry point:** `python app/http-server.py <PORT>` (e.g., `python app/http-server.py 8085`).
- **Deps:** `pip install -r requirements.txt`.
- Flask debug mode is hardcoded off.

## Architecture Notes
- **App Factory:** `app/__init__.py` (`create_app`). Registers blueprints, Swagger, CORS, CSRF, and auth.
- **Blueprints:** Each domain has its own blueprint in `app/api/routes/`. Routes no longer live in a single monolithic file.
- **Extensions:** Flask extensions (CSRF, CORS, HTTP Basic Auth) are instantiated in `app/extensions.py` and bound to the app in the factory.
- **Config:** `app/config.py` centralizes all environment variable reads.
- **Repositories:** `app/infrastructure/persistence/mysql_repositories.py` provides concrete MySQL access through interfaces defined in `app/domain/interfaces/`.
- **Security:** `app/infrastructure/security/basic_auth.py` implements user verification against the DB using the abstract `IUserRepository`.
- **Legacy:** Original business-logic modules were moved to `app/legacy/` with fixed cross-imports (`app.legacy.xxx`). Blueprints delegate to them while the new architecture matures.

## Docker Quirks
- `.dockerignore` ignores **everything except `requirements.txt`**. The Docker image does **not** contain application code.
- `docker-compose.yml` mounts `./app` at runtime and expects a **sibling `../envs/` directory** containing:
  - `file.env` (env vars)
  - `file.aws_credentials` (AWS credentials)
- These `envs/` files are not versioned and are required for local Docker runs.

## Environment & Secrets
The app reads all config from environment variables. Key groups:
- `HOST_BD`, `PORT_BD`, `USER_BD`, `PASS_BD`, `SCHEMA_BD` — MySQL via `pymysql`.
- `SECRET_KEY_CSRF` — Flask CSRF.
- Various API keys: `NOTIFICATION_URL`, `AWS_PINPOINT_APP_ID`, `ATTLASIAN_TOKEN`, `WAZA_BEARER_TOKEN`, `CHATBOT_API_KEY`, etc.

## Testing & Quality
- **Run tests:** `pytest` (from repo root). Config in `pytest.ini` enforces `--cov-fail-under=60`.
- **Test structure:** `tests/unit/` mirroring the `app/` layers. Uses `conftest.py` with Flask app/test-client fixtures and `mock_pymysql`.
- **Coverage target:** ~60%+. Most legacy modules are tested with mocks (pymysql, requests, boto3, imaplib).
- **No lint, formatter, or typechecker config** (no `flake8`, `black`, `mypy`, `ruff`).
- CI only builds the Docker image and runs SonarQube/CodeQL analysis.

## CI/CD
- GitHub Actions trigger on `push` / `pull_request` to `main` and `develop`.
- Workflows: Docker image build (`docker-image.yml`), SonarQube (`sonarqube.yml`), CodeQL (`codeql.yml`).
