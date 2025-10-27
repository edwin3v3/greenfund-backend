import os
from sqlmodel import create_engine, SQLModel, Session, select, func # <-- Import select, func
from dotenv import load_dotenv
from app.models import Badge # <-- Import Badge model

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The `connect_args` is only needed for SQLite
engine_args = {}
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

# Ensure DATABASE_URL is loaded before creating the engine
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

engine = create_engine(DATABASE_URL, echo=True, **engine_args)

def create_db_and_tables():
    """
    Initializes the database by creating all tables defined by SQLModel models,
    and seeds initial data like badges.
    This function is called once on application startup.
    """
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Database tables created.")

    # --- vvvv SEED INITIAL BADGES vvvv ---
    print("Seeding initial badges...")
    try:
        with Session(engine) as session:
            badges_to_seed = [
                {"name": "First Farm", "description": "Awarded for adding your first farm.", "icon_name": "FiMapPin"},
                {"name": "Soil Analyst", "description": "Awarded for submitting your first soil analysis report.", "icon_name": "FiDroplet"},
                {"name": "Community Member", "description": "Awarded for creating your first forum thread.", "icon_name": "FiUsers"},
                {"name": "Climate Watcher", "description": "Awarded for viewing a climate action report.", "icon_name": "FiCloudDrizzle"},
            ]

            # Check if badges already exist before attempting to seed
            existing_badge_count = session.exec(select(func.count(Badge.id))).one_or_none()

            # Handle case where table might not exist yet fully during first setup
            if existing_badge_count is None:
                 existing_badge_count = 0

            if existing_badge_count == 0:
                 print("No badges found, seeding...")
                 for badge_data in badges_to_seed:
                      # Double-check existence just in case
                      existing = session.exec(select(Badge).where(Badge.name == badge_data["name"])).first()
                      if not existing:
                          badge = Badge(**badge_data)
                          session.add(badge)
                          print(f"  Added badge: {badge_data['name']}")
                 session.commit()
                 print("Initial badges seeded.")
            else:
                 print(f"Found {existing_badge_count} existing badges, skipping seed.")

    except Exception as e:
        print(f"Error seeding badges: {e}")
        # Depending on the error, you might want to rollback the session
        # session.rollback() # If using the session from `with Session(engine)...`
    # --- ^^^^ END SEEDING ^^^^ ---

def get_db():
    """
    A FastAPI dependency that provides a database session per request.
    It ensures the session is always closed after the request is finished.
    """
    with Session(engine) as session:
        yield session