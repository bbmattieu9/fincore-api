from sqlalchemy import create_engine, MetaData
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

# Naming convention (for Alembic)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# Engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base
Base = declarative_base(metadata=metadata)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()