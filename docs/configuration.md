# Configuration

There are two different mechanisms for configuration in this project, and
they serve different purposes. Don't confuse them.

## `.flaskenv` — Flask CLI bootstrapping

```
FLASK_APP=app.app
FLASK_DEBUG=1
```

- Tells the `flask` CLI (`flask run`, `flask shell`, `flask routes`) *where
  to find* the app, before it can do anything else.
- **Committed to git.** Nothing in here is a secret — it's just "how do you
  run this project," which should be identical for every developer.
- Only affects the `flask` CLI. If you run the app another way (e.g.
  `python app/app.py`, gunicorn), this file has no effect.
- Requires `python-dotenv` to be installed for Flask to auto-load it
  (already a dependency here).

## `.env` — secrets and per-environment overrides

```
SECRET_KEY=some-real-secret-value
DATABASE_URL=postgresql://user:pass@host/dbname
```

- **Never committed** — already in `.gitignore`.
- This is where real secrets and machine/environment-specific values go.
- Currently empty in this repo (development falls back to the defaults in
  `config.py`). Before deploying anywhere real, at minimum set a proper
  `SECRET_KEY` here.

## `app/config.py` — the actual config classes

```python
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///.../app.db")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    GOOGLE_APPLICATION_CREDENTIALS = {...}  # service-account JSON

class DevelopmentConfig(Config): DEBUG = True
class TestingConfig(Config): TESTING = True; SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
class ProductionConfig(Config): DEBUG = False
```

`create_app(config_name)` picks a class from the `config` dict by name. This
is where `os.environ.get(...)` reads whatever `.env`/your shell set, with a
fallback default for local dev.

**Adding a new config value:**

1. Add it to the `Config` base class (or a specific subclass if it should
   only apply to one environment), reading from `os.environ` with a sane
   default.
2. If it's a secret, document it in `.env.example` (see below) — don't hardcode
   the real value anywhere in the class.
3. Access it anywhere in the app via `current_app.config["YOUR_KEY"]`.

`GOOGLE_APPLICATION_CREDENTIALS` contains the parsed service-account JSON.
The `GOOGLE_APPLICATION_CREDENTIALS` environment variable may point to a
different JSON file; otherwise the app looks for
`GOOGLE_APPLICATION_CREDENTIALS.json` in the project root. Use it for Google
API clients, for example:

```python
from flask import current_app

credentials_info = current_app.config["GOOGLE_APPLICATION_CREDENTIALS"]
project_id = credentials_info["project_id"]
```

This service-account configuration is not used for Google user sign-in.
`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` remain separate web OAuth
credentials and belong in `.env`.

## Precedence, if you're running through the `flask` CLI

`.env` loads first, then `.flaskenv` — but you shouldn't need to rely on
that, since the two files shouldn't define overlapping variables in the
first place.

## Recommended: add a `.env.example`

This repo doesn't have one yet, but you should add one whenever you add a
new required `.env` variable — commit `.env.example` (no real values) so
teammates know what to fill in locally:

```
SECRET_KEY=
DATABASE_URL=
```
