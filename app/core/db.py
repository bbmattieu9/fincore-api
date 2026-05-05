from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

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

# ================= DATABASE URL =================

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=MYSQL_USER,
    password=MYSQL_PASSWORD,  # raw password (handled safely by SQLAlchemy)
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    database=MYSQL_DATABASE,
)

# ================= NAMING CONVENTION (ALEMBIC SAFE) =================

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# ================= ENGINE =================

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

# ================= SESSION =================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ================= BASE =================

Base = declarative_base(metadata=metadata)

# ================= DEPENDENCY =================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()