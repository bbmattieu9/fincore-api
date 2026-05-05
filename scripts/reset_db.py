from sqlalchemy import create_engine, text
from app.core.db import (
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_DATABASE
)

#  SAFETY CHECK (PUT IT HERE)
confirm = input("This will DELETE the database. Continue? (yes/no): ")
if confirm.lower() != "yes":
    print("Cancelled.")
    exit()

# Connect WITHOUT specifying database
BASE_DB_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"

engine = create_engine(BASE_DB_URL)

with engine.connect() as conn:
    conn.execute(text(f"DROP DATABASE IF EXISTS {MYSQL_DATABASE}"))
    conn.execute(text(f"CREATE DATABASE {MYSQL_DATABASE}"))

print(" [ __Database reset complete__ ]")

# USAGE ==> py scripts/reset_db.py