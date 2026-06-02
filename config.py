import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    _uri = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    if _uri.startswith('postgres://'):
        _uri = _uri.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    PROGRAM_START_DATE = os.environ.get('PROGRAM_START_DATE', '2026-06-02')
