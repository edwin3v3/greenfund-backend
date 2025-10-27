from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from typing import List

from app.database import get_db
from app.models import User, Badge, UserBadge
from app.schemas import UserBadgeRead, BadgeCountResponse, BadgeRead
from app.security import get_current_user

router = APIRouter(prefix="/badges", tags=["Badges"])

@router.get("/", response_model=List[BadgeRead])
def get_all_available_badges(db: Session = Depends(get_db)):
    """
    Get a list of all possible badges in the system.
    """
    badges = db.exec(select(Badge)).all()
    return badges

@router.get("/me", response_model=List[UserBadgeRead])
def get_my_earned_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of all badges earned by the current user.
    """
    user_badges = db.exec(
        select(UserBadge)
        .where(UserBadge.user_id == current_user.id)
        .order_by(UserBadge.earned_at.desc())
    ).all()
    
    return user_badges

@router.get("/me/count", response_model=BadgeCountResponse)
def get_my_badge_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the total count of badges earned by the current user.
    (This is for the dashboard card)
    """
    # This query counts the rows in UserBadge for the current user
    count = db.exec(
        select(func.count(UserBadge.badge_id))
        .where(UserBadge.user_id == current_user.id)
    ).one()
    
    return BadgeCountResponse(count=count)


# --- Test Endpoint (So you can see it work) ---
@router.post("/me/award_test/{badge_name}", response_model=UserBadgeRead)
def award_test_badge(
    badge_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    TESTING ONLY: Manually award a badge to the current user by name.
    """
    # 1. Find the badge in the DB
    badge = db.exec(select(Badge).where(Badge.name == badge_name)).first()
    if not badge:
        raise HTTPException(status_code=404, detail=f"Badge '{badge_name}' not found. Create it first.")

    # 2. Check if user already has it
    existing_link = db.get(UserBadge, (current_user.id, badge.id))
    if existing_link:
        return existing_link # User already has this badge

    # 3. Award the badge
    new_badge_link = UserBadge(user_id=current_user.id, badge_id=badge.id)
    db.add(new_badge_link)
    db.commit()
    db.refresh(new_badge_link)
    return new_badge_link