from sqlmodel import Field, Relationship, SQLModel, JSON
from sqlalchemy import Column
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone
from pydantic import EmailStr # Need EmailStr for User model

# --- Forward References ---
# This helps prevent circular import errors
if TYPE_CHECKING:
    # Added Notification here
    from .models import User, Farm, FarmActivity, SoilReport, ForumThread, ForumPost, Badge, UserBadge, Notification 

# --- User Model ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: Optional[str] = None
    email: EmailStr = Field(unique=True, index=True) 
    hashed_password: str
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # --- Relationships ---
    farms: List["Farm"] = Relationship(back_populates="owner")
    activities: List["FarmActivity"] = Relationship(back_populates="user")
    threads: List["ForumThread"] = Relationship(back_populates="owner")
    posts: List["ForumPost"] = Relationship(back_populates="owner")
    # --- Renamed badge_links -> badges for consistency ---
    badges: List["UserBadge"] = Relationship(back_populates="user") 
    # --- ADDED: Relationship to Notifications ---
    notifications: List["Notification"] = Relationship(back_populates="user")
    # --- END ADDITION ---

# --- Farm Model ---
class Farm(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    location_text: str
    latitude: Optional[float] = None 
    longitude: Optional[float] = None 
    size_acres: Optional[float] = None 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_crop: Optional[str] = Field(default=None, index=True)

    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="farms")

    activities: List["FarmActivity"] = Relationship(back_populates="farm")
    soil_reports: List["SoilReport"] = Relationship(back_populates="farm")


# --- FarmActivity Model ---
class FarmActivity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity_type: str
    description: Optional[str] = None
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    carbon_footprint_kg: Optional[float] = None
    value: Optional[float] = None
    unit: Optional[str] = None

    farm_id: int = Field(foreign_key="farm.id")
    farm: "Farm" = Relationship(back_populates="activities")
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="activities")

# --- SoilReport Model ---
class SoilReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ph: Optional[float] = Field(default=None)
    nitrogen: Optional[float] = Field(default=None)
    phosphorus: Optional[float] = Field(default=None)
    potassium: Optional[float] = Field(default=None)
    moisture: Optional[float] = Field(default=None)
    ai_analysis_text: Optional[str] = None
    suggested_crops: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))

    farm_id: int = Field(foreign_key="farm.id")
    farm: "Farm" = Relationship(back_populates="soil_reports")


# --- ForumThread Model ---
class ForumThread(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="threads")

    posts: List["ForumPost"] = Relationship(back_populates="thread")

# --- ForumPost Model ---
class ForumPost(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="posts")

    thread_id: int = Field(foreign_key="forumthread.id")
    thread: "ForumThread" = Relationship(back_populates="posts")
    
    # --- ADDED: Relationship to Notifications ---
    notifications: List["Notification"] = Relationship(back_populates="post")
    # --- END ADDITION ---


# --- Badge Models ---
class Badge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True) 
    description: str              
    icon_name: Optional[str] = None   
    user_links: List["UserBadge"] = Relationship(back_populates="badge")

class UserBadge(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    badge_id: int = Field(foreign_key="badge.id", primary_key=True)
    earned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # --- Renamed badge_links -> user ---
    user: "User" = Relationship(back_populates="badges") 
    badge: "Badge" = Relationship(back_populates="user_links")


# --- vvvv NEW NOTIFICATION MODEL vvvv ---
class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True) # User TO notify
    message: str
    is_read: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Link to the post that triggered it (nullable in case of system notifications later)
    post_id: Optional[int] = Field(default=None, foreign_key="forumpost.id") 
    
    # Relationships
    user: "User" = Relationship(back_populates="notifications")
    post: Optional["ForumPost"] = Relationship(back_populates="notifications")
# --- ^^^^ END NEW MODEL ^^^^ ---