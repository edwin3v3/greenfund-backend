from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func, desc  # Import desc
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone

from app.database import get_db
# Import Farm model
from app.models import FarmActivity, User, Farm
from app.schemas import FarmActivityCreate, FarmActivityRead, WeeklyEmissionsResponse
from app.security import get_current_user
from app.carbon_model import estimate_carbon_with_ai

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.post("/", response_model=FarmActivityRead, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity: FarmActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.get(Farm, activity.farm_id)
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    estimated_carbon = await estimate_carbon_with_ai(
        activity.activity_type,
        activity.value,
        activity.unit,
        activity.description
    )

    activity_data = activity.model_dump()
    if activity_data.get("date") is None:
        activity_data["date"] = datetime.now(timezone.utc)
    activity_data["user_id"] = current_user.id
    activity_data["carbon_footprint_kg"] = estimated_carbon

    try:
        db_activity = FarmActivity.model_validate(activity_data)
    except Exception as e:
        print(f"ERROR: Validation failed for FarmActivity: {e}")
        print(f"Data causing validation error: {activity_data}")
        raise HTTPException(
            status_code=422, detail=f"Invalid activity data: {e}")

    try:
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to save activity to DB: {e}")
        raise HTTPException(
            status_code=500, detail="Could not save activity to database.")


@router.get("/farm/{farm_id}", response_model=List[FarmActivityRead])
def get_activities_for_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.get(Farm, farm_id)
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Farm not found")

    activities = db.exec(
        select(FarmActivity)
        .where(FarmActivity.farm_id == farm_id)
        .order_by(desc(FarmActivity.date))
    ).all()
    return activities

# --- vvvv ADD THIS NEW ENDPOINT vvvv ---


@router.get("/me/recent", response_model=List[FarmActivityRead])
def get_my_recent_activities(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the most recent activities from ALL of the user's farms.
    """
    # Get all farm IDs owned by the current user
    user_farm_ids = db.exec(
        select(Farm.id).where(Farm.owner_id == current_user.id)
    ).all()

    if not user_farm_ids:
        return []  # Return empty list if user has no farms

    # Fetch the most recent activities from any of the user's farms
    activities = db.exec(
        select(FarmActivity)
        .where(FarmActivity.farm_id.in_(user_farm_ids))
        .order_by(desc(FarmActivity.date))
        .limit(limit)
    ).all()

    return activities
# --- ^^^^ END NEW ENDPOINT ^^^^ ---


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... (delete logic) ...
    activity = db.get(FarmActivity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    if activity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(activity)
    db.commit()
    return

# ... (CarbonSummary class) ...


class CarbonSummary(BaseModel):
    total_carbon_kg: float
    breakdown_by_activity: Dict[str, float]


@router.get("/farm/{farm_id}/carbon_summary", response_model=CarbonSummary)
def get_carbon_summary_for_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... (carbon summary logic) ...
    farm = db.get(Farm, farm_id)
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Farm not found")

    total_carbon = db.exec(
        select(func.sum(FarmActivity.carbon_footprint_kg))
        .where(FarmActivity.farm_id == farm_id)
    ).first()

    breakdown_query = db.exec(
        select(
            FarmActivity.activity_type,
            func.sum(FarmActivity.carbon_footprint_kg)
        )
        .where(FarmActivity.farm_id == farm_id)
        .group_by(FarmActivity.activity_type)
    ).all()

    breakdown_dict = {activity: carbon for activity,
                      carbon in breakdown_query if carbon is not None}

    return CarbonSummary(
        total_carbon_kg=total_carbon or 0.0,
        breakdown_by_activity=breakdown_dict
    )


@router.get("/emissions/weekly", response_model=WeeklyEmissionsResponse)
def get_weekly_emissions_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... (weekly emissions logic) ...
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=6)
    user_farm_ids_query = select(Farm.id).where(
        Farm.owner_id == current_user.id)
    user_farm_ids = db.exec(user_farm_ids_query).all()

    if not user_farm_ids:
        return WeeklyEmissionsResponse(total_emissions_kg=0.0, daily_emissions=[0.0]*7)

    start_datetime = datetime.combine(
        seven_days_ago, datetime.min.time(), tzinfo=timezone.utc)
    end_datetime = datetime.combine(
        today, datetime.max.time(), tzinfo=timezone.utc)

    activities = db.exec(
        select(FarmActivity)
        .where(FarmActivity.farm_id.in_(user_farm_ids))
        .where(FarmActivity.date >= start_datetime)
        .where(FarmActivity.date <= end_datetime)
    ).all()

    daily_totals = {(seven_days_ago + timedelta(days=i)): 0.0 for i in range(7)}
    total_emissions = 0.0

    for activity in activities:
        activity_date = activity.date.astimezone(timezone.utc).date()
        if activity_date in daily_totals:
            footprint = activity.carbon_footprint_kg or 0.0
            daily_totals[activity_date] += footprint
            total_emissions += footprint

    daily_emissions_list = [
        daily_totals[seven_days_ago + timedelta(days=i)] for i in range(7)]

    return WeeklyEmissionsResponse(
        total_emissions_kg=round(total_emissions, 2),
        daily_emissions=daily_emissions_list
    )
