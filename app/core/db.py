from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, MetaData
# from sqlalchemy.engine import URL
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

# ================= DATABASE URL =================
encoded_password = quote_plus(MYSQL_PASSWORD)
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

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
    "mysql+pymysql://root:MyF%40stAPI2026%21@127.0.0.1:3306/fastapi_db",
    echo=True
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


# print("USER:", MYSQL_USER)
# print("PASSWORD:", MYSQL_PASSWORD)
# print("HOST:", MYSQL_HOST)
# print("PORT:", MYSQL_PORT)
# print("DB:", MYSQL_DATABASE)
# print("DATABASE_URL:", DATABASE_URL)