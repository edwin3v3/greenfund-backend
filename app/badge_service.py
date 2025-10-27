# app/badge_service.py (New File)

from sqlmodel import Session, select
from app.models import User, Badge, UserBadge, Farm
from datetime import datetime

def award_badge(db: Session, user_id: int, badge_name: str):
    """Awards a badge to a user if they don't already have it."""
    
    # 1. Find the badge (e.g., "First Farm Added")
    badge = db.exec(select(Badge).where(Badge.name == badge_name)).first()
    if not badge:
        # Note: In a real app, you might log an error here
        print(f"Badge '{badge_name}' not found in database.")
        return None

    # 2. Check if user already has this specific badge
    existing_link = db.get(UserBadge, (user_id, badge.id))
    if existing_link:
        return existing_link # Already awarded

    # 3. Award the badge
    new_badge_link = UserBadge(user_id=user_id, badge_id=badge.id, earned_at=datetime.utcnow())
    db.add(new_badge_link)
    db.commit()
    db.refresh(new_badge_link)
    print(f"Successfully awarded badge: {badge_name} to user {user_id}")
    return new_badge_link

def check_and_award_new_farm_badges(db: Session, user_id: int):
    """Checks farm count and awards related badges."""
    
    # Check Farm Count
    farm_count_statement = select(Farm).where(Farm.owner_id == user_id)
    farm_count = len(db.exec(farm_count_statement).all())

    if farm_count >= 1:
        # Example: Award 'First Farm' badge
        award_badge(db, user_id, "First Farm Pioneer")
    
    if farm_count >= 5:
        # Example: Award 'Farm Tycoon' badge
        award_badge(db, user_id, "Farm Tycoon")
        
    # Add more badge rules here...