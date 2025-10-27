# GreenFund-test-Backend/app/schemas.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel

# --- User Schemas ---


class UserBase(SQLModel):
    email: EmailStr
    full_name: Optional[str] = None
    location: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    location: Optional[str] = None


# --- Farm Schemas ---
# ... (Farm Schemas) ...
class FarmBase(SQLModel):
    name: str
    location_text: str
    size_acres: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    current_crop: Optional[str] = None


class FarmCreate(FarmBase):
    pass


class FarmRead(FarmBase):
    id: int
    owner_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# --- Token Schemas ---
# ... (Token Schemas) ...
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# --- FarmActivity Schemas ---
# ... (FarmActivity Schemas) ...
class FarmActivityBase(SQLModel):
    activity_type: str
    description: Optional[str] = None
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    value: Optional[float] = None
    unit: Optional[str] = None


class FarmActivityCreate(FarmActivityBase):
    farm_id: int


class FarmActivityRead(FarmActivityBase):
    id: int
    farm_id: int
    user_id: int
    carbon_footprint_kg: Optional[float] = None
    date: datetime
    model_config = ConfigDict(from_attributes=True)


# --- SoilReport Schemas ---
# ... (SoilReport Schemas) ...
class SoilReportBase(SQLModel):
    ph: Optional[float] = None
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    moisture: Optional[float] = None


class SoilReportCreate(SoilReportBase):
    farm_id: int


class SoilReportRead(SoilReportBase):
    id: int
    farm_id: int
    date: datetime
    ai_analysis_text: Optional[str] = None
    suggested_crops: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


# --- Forum Schemas ---
# ... (Forum Schemas) ...
class ForumUserBase(BaseModel):
    id: int
    full_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ForumPostBase(BaseModel):
    content: str = Field(min_length=1)


class ForumPostCreate(ForumPostBase):
    thread_id: int


class ForumPostRead(ForumPostBase):
    id: int
    created_at: datetime
    owner: ForumUserBase
    model_config = ConfigDict(from_attributes=True)


class ForumThreadBase(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    content: str = Field(min_length=10)


class ForumThreadCreate(ForumThreadBase):
    pass


class ForumThreadReadBasic(ForumThreadBase):
    id: int
    created_at: datetime
    owner: ForumUserBase
    posts: List[ForumPostRead] = []
    model_config = ConfigDict(from_attributes=True)


class ForumThreadReadWithPosts(ForumThreadReadBasic):
    posts: List[ForumPostRead] = []
    model_config = ConfigDict(from_attributes=True)


# --- Climate Action Schemas ---
# ... (Climate Action Schemas) ...
class Alert(BaseModel):
    type: str
    name: str
    risk_level: str
    advice: str


class PestDiseaseAlertResponse(BaseModel):
    farm_id: int
    alerts: List[Alert]


class CarbonGuidanceResponse(BaseModel):
    farm_id: int
    guidance: dict


class WaterAdviceResponse(BaseModel):
    farm_id: int
    advice: dict


# --- Badge Schemas ---
# ... (Badge Schemas) ...
class BadgeRead(BaseModel):
    id: int
    name: str
    description: str
    icon_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class UserBadgeRead(BaseModel):
    earned_at: datetime
    badge: BadgeRead
    model_config = ConfigDict(from_attributes=True)


class BadgeCountResponse(BaseModel):
    count: int

# --- vvvv ADD THIS NEW SCHEMA vvvv ---


class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str
# --- ^^^^ END NEW SCHEMA ^^^^ ---


class WeeklyEmissionsResponse(BaseModel):
    total_emissions_kg: float
    daily_emissions: List[float]  # List of 7 values, oldest to newest
    # Optional: % change vs previous week
    trend_percent: Optional[float] = None


class CropSuggestionSummaryResponse(BaseModel):
    unique_suggestion_count: int
    # List of the 3 most recent unique suggestions
    recent_suggestions: List[str]


class NotificationRead(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime
    post_id: Optional[int] = None  # Include post_id if available
    model_config = ConfigDict(from_attributes=True)
