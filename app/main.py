import os # <-- 1. Import os
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # <-- Import StaticFiles

from app.database import create_db_and_tables
from app.routers import (
    auth, users, farms, climate, activities,
    soil, forum, climate_actions, chatbot,
    badges, notifications
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up and creating database tables...")
    create_db_and_tables()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# --- vvvv UPDATED CORS vvvv ---
# Get the production frontend URL from the environment
# Default to localhost for local development
prod_origin = os.getenv("CORS_ORIGIN", "http://localhost:5173")

origins = [
    prod_origin,             # The live frontend URL (e.g., https://greenfund.onrender.com)
    "http://localhost:5173", # Keep localhost for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # <-- Use the dynamic origins list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- ^^^^ END CORS UPDATE ^^^^ ---

# --- Mount Static Files ---
# This makes /static/farm_images/... work
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- ROUTER CONFIGURATION ---
api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(farms.router)
api_router.include_router(climate.router)
api_router.include_router(activities.router)
api_router.include_router(soil.router)
api_router.include_router(forum.router)
api_router.include_router(climate_actions.router)
api_router.include_router(chatbot.router)
api_router.include_router(badges.router)
api_router.include_router(notifications.router)

app.include_router(api_router)
# --- END ROUTER CONFIGURATION ---


@app.get("/")
def read_root():
    return {"message": "Welcome to the GreenFund API"}