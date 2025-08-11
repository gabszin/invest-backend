from logging.config import fileConfig
from alembic import context
import os
from sqlalchemy import create_engine
from app.db import Base
from app import models  # noqa: F401

# Config Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Converte a URL assíncrona em síncrona (para migrações)
ASYNC_URL = os.getenv("DATABASE_URL", "")
if not ASYNC_URL:
    raise RuntimeError("DATABASE_URL não definido no ambiente")
SYNC_URL = ASYNC_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")

def run_migrations_offline():
    context.configure(
        url=SYNC_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(SYNC_URL, future=True)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()