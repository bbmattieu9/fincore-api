from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

from app.core.config import (
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DATABASE
)

# Validate config
if not MYSQL_PASSWORD:
    raise ValueError("Database credentials not set")

# Encode password
encoded_password = quote_plus(MYSQL_PASSWORD)

# Connection string
DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{encoded_password}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# Engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True
)

# Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()