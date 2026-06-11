import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    _uri = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    # Normalise URL and add psycopg3 dialect for all PostgreSQL connections
    if _uri.startswith('postgres://'):
        _uri = _uri.replace('postgres://', 'postgresql+psycopg://', 1)
    elif _uri.startswith('postgresql://'):
        _uri = _uri.replace('postgresql://', 'postgresql+psycopg://', 1)
    # Strip query params — SSL and schema are set via engine options below
    _base_uri = _uri.split('?')[0] if '?' in _uri else _uri

    SQLALCHEMY_DATABASE_URI = _base_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    PROGRAM_START_DATE = os.environ.get('PROGRAM_START_DATE', '2026-06-02')

    # Session configuration
    SESSION_COOKIE_SECURE = True  # Only send over HTTPS in production
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 0  # Session expires when browser closes
    WTF_CSRF_TIME_LIMIT = None  # No time limit on CSRF tokens

    if 'postgresql' in _base_uri:
        _schema = os.environ.get('DB_SCHEMA', 'public')
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 280,
            'connect_args': {
                'sslmode': 'require',
                'options': f'-csearch_path={_schema}',
            },
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {}
