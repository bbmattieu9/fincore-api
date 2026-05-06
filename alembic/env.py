from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context

from app.core.db import DATABASE_URL, Base
from app.models import user, account, transaction  # ensure models are registered

# ================= ALEMBIC CONFIG =================

config = context.config

# Fix for % issue in passwords
config.set_main_option(
    "sqlalchemy.url",
    str(DATABASE_URL).replace("%", "%%")
)

# ================= METADATA =================

target_metadata = Base.metadata

# ================= LOGGING =================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ================= OFFLINE MODE =================

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ================= ONLINE MODE =================
def run_migrations_online() -> None:
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()
# ================= ENTRY =================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()