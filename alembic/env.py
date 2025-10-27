import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel # Import SQLModel
from dotenv import load_dotenv # Import dotenv

# --- This block loads your .env file to get the DB_URL ---
# Add the project root (one level up from /alembic) to the sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Load environment variables from .env file
load_dotenv()
# --- End block ---

# --- IMPORT YOUR MODELS ---
# This line is CRITICAL for autogenerate to find your tables
# It imports all models from your app/models.py file
from app.models import *
# --- END IMPORT ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- THIS IS THE MOST IMPORTANT PART ---
# Set the target_metadata to your SQLModel.metadata
# This tells Alembic what tables *should* exist
target_metadata = SQLModel.metadata
# --- END IMPORTANT PART ---

def get_url():
    """Returns the database URL from the environment variable."""
    # Alembic reads sqlalchemy.url from alembic.ini, which has %(DB_URL)s
    # We must provide DB_URL. We load it from .env at the top.
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set. Check your .env file.")
    return db_url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create a new configuration dictionary for the engine
    # and add the database URL
    
    # --- THIS IS THE FIX ---
    # Changed config.config_main_section to config.config_ini_section
    configuration = config.get_section(config.config_ini_section, {})
    # --- END FIX ---

    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()