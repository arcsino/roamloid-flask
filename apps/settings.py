import os
from pathlib import Path
from dotenv import load_dotenv


# Base directory of the project
BASEDIR = Path(__file__).resolve().parent.parent

# Load environment variables from a .env file if it exists
load_dotenv(BASEDIR / ".env")

# Secret key for session management and other security-related needs
# SECRET_KEY = os.urandom(24)
# 秘密鍵を固定の値(.envのSECRET_KEY)にすることで、サーバー再起動後もセッションが維持されるようにする⇖はサーバーー再起動のたびに変わってしまうため
SECRET_KEY = os.getenv("SECRET_KEY", "default_fallback_key_for_development")

# Debug mode
DEBUG = os.getenv("DEBUG", 0)

# Database configuration
SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASEDIR / 'db.sqlite3'}"
# When using PostgreSQL, uncomment the following line and update the credentials
# SQLALCHEMY_DATABASE_URI = f"postgresql://user:password@localhost/dbname"

# CORS configuration
CORS_ORIGINS = os.getenv("FLASK_CORS_ORIGINS", "").split(",")

# Japanese characters support
JSON_AS_ASCII = False
