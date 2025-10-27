import os
from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The `connect_args` is only needed for SQLite to support multithreading.
# It is not used by PostgreSQL.
engine_args = {}
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=True, **engine_args)


def create_db_and_tables():
    """
    Initializes the database by creating all tables defined by SQLModel models.
    This function is called once on application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_db():
    """
    A FastAPI dependency that provides a database session per request.
    It ensures the session is always closed after the request is finished.
    """
    with Session(engine) as session:
        yield session
