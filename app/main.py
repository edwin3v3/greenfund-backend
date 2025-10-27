from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import (
    auth, users, farms, climate, activities,
    soil, forum, climate_actions, chatbot,
    badges, notifications  # <-- 1. Import the 'notifications' router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up and creating database tables...")
    create_db_and_tables()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# CORS Middleware
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER CONFIGURATION ---
# Create a main router for the /api prefix
api_router = APIRouter(prefix="/api")

# Include all the individual routers into the main api_router
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
# <-- 2. Include the 'notifications' router
api_router.include_router(notifications.router)

# Include the single api_router into the main app
app.include_router(api_router)
# --- END ROUTER CONFIGURATION ---


@app.get("/")
def read_root():
    return {"message": "Welcome to the GreenFund API"}
