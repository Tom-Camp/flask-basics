import os
from pathlib import Path

from app.utils.helpers import BASE_DIR, load_json


class Config:
    # An empty/blank DATABASE_URL (as shipped in .env.example) means
    # "use the local SQLite default", not "use an empty URI".
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL", "").strip()
        or f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    FLASK_APP = os.environ.get("FLASK_APP", "app")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", False)
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")

    # OAuth 2.0 "Web application" client credentials from Google Cloud
    # Console (APIs & Services -> Credentials). Sign-in uses these, not
    # GOOGLE_API_KEY. See docs/authentication.md.
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")

    # This is a service-account key for Google APIs. It is intentionally kept
    # separate from the web OAuth credentials above.
    _credentials_path = Path(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        or BASE_DIR / "GOOGLE_APPLICATION_CREDENTIALS.json"
    )
    GOOGLE_APPLICATION_CREDENTIALS = (
        load_json(_credentials_path) if _credentials_path.is_file() else {}
    )


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Tests run same-origin and don't exercise the CSRF threat model
    # (see docs/forms.md).
    WTF_CSRF_ENABLED = False

    GOOGLE_APPLICATION_CREDENTIALS = {}


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
