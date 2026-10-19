# Copilot instructions

Flask learning project (Python >=3.14, SQLite). Deep-dive guides live in `docs/` — start with `docs/architecture.md`.

## Commands

Everything runs through `uv` (no plain `pip`/`venv`).

```bash
uv sync                                  # install deps
uv run flask db upgrade                  # apply migrations (creates instance/app.db)
uv run flask run                         # dev server (.flaskenv sets FLASK_APP=app.app)
uv run flask routes                      # list registered routes
uv run flask db migrate -m "message"     # generate migration after model change
uv run pytest                            # full suite
uv run pytest tests/test_auth.py::test_name -v   # single test
uv run pytest --cov=app --cov-report=term-missing
uv run prek run --all-files              # lint/format/type/security hooks
uv add <package>                         # add dependency (updates pyproject.toml + uv.lock)
```

Linting is via prek (pre-commit format) hooks: ruff (`--fix` + format), mypy, bandit (`-c .bandit`), and file checks. Run `uv run prek install --overwrite` once to enable hooks.

Commit messages must be Conventional Commits (enforced by a commitizen `commit-msg` hook): `feat|fix|build|bump|chore|ci|docs|perf|refactor|revert|style|test(scope): description`.

## Architecture

- **App factory**: `app/__init__.py:create_app(config_name)` builds the app; `app/app.py` is the thin entrypoint (`app = create_app()`). Config is chosen by `FLASK_ENV` (default → `DevelopmentConfig`); classes in `app/config.py`.
- **Extensions** (`app/extensions.py`) are created unbound (`dbase`, `migrate`, `login_manager`, `csrf`, `oauth`) and bound in `create_app()`. Import them from there to avoid circular imports. The database instance is named `dbase`, not `db`.
- **Blueprints** are imported inside `create_app()` and registered there: `app/main` (package), plus `app/routes/{auth,resume,users}_routes.py`. New blueprints must be registered in `create_app()`.
- **Layers**: routes → `app/services/` (business logic, e.g. `users_service.py`) → `app/models/`; WTForms in `app/forms/`; pydantic-ai/Google resume parsing in `app/ai/`.
- **Auth**: Flask-Login sessions + Authlib Google OIDC (client registered in `create_app()`, credentials from `GOOGLE_CLIENT_ID/SECRET`). Unauthenticated users are redirected to `auth.login`. See `docs/authentication.md`.
- **Config/secrets**: `.env` (gitignored) for secrets, `.flaskenv` for the flask CLI, `config.py` for defaults. A blank `DATABASE_URL` means the SQLite default. `GOOGLE_APPLICATION_CREDENTIALS.json` (gitignored) is a service-account key separate from the OAuth credentials.

## Conventions

- **Models** subclass `BaseModel` (`app/models/base.py`, gives `id`/`created_at`/`updated_at`), which derives from the typed `Base` in `app/extensions.py` — never subclass `dbase.Model` (breaks mypy). Use SQLAlchemy 2.0 `Mapped`/`mapped_column`.
- **New models must be imported in `app/models/__init__.py`**, otherwise they don't register in metadata and Alembic won't see them. Then generate and commit a migration in `migrations/versions/`.
- **Schema changes** go through Flask-Migrate in dev/prod; only the `TESTING` config uses `dbase.create_all()` on an in-memory SQLite db.
- **Templates**: `base.html` layout, `partials/` (nav, footer), `pages/`. `current_year` is injected globally via a context processor. `Post.body` is rendered with `|safe` (raw HTML) — don't feed it untrusted content.
- **Tests** use fixtures in `tests/conftest.py` (`app` with `create_app("testing")`, `client`, `db`). CSRF is disabled in `TestingConfig`. **Never define models inside test functions** — `db.metadata` is process-global and shared across tests (see `docs/testing.md`).
- mypy ignores missing stubs for `flask_login` and `flask_wtf` (see `pyproject.toml`).
