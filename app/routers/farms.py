from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func # <-- 1. Import 'func'
from typing import List

from app.database import get_db
# 2. Import Badge and UserBadge
from app.models import Farm, User, Badge, UserBadge 
from app.schemas import FarmCreate, FarmRead
from app.security import get_current_user
from app.utils import get_coords_from_location 

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post("/", response_model=FarmRead, status_code=status.HTTP_201_CREATED)
async def create_farm(
    farm: FarmCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    coords = await get_coords_from_location(farm.location_text)
    if not coords:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not find coordinates for location: '{farm.location_text}'."
        )

    farm_data = farm.model_dump()
    farm_data.update(coords)
    farm_data["owner_id"] = current_user.id

    db_farm = Farm.model_validate(farm_data)

    try:
        db.add(db_farm)
        db.commit()
        db.refresh(db_farm)
    except Exception as e:
        db.rollback()
        print(f"Error creating farm: {e}")
        raise HTTPException(status_code=500, detail="Error creating farm")

    # --- vvvv NEW BADGE LOGIC vvvv ---
    try:
        # Check how many farms this user owns
        farm_count = db.exec(
            select(func.count(Farm.id))
            .where(Farm.owner_id == current_user.id)
        ).one()

        if farm_count == 1:
            # This is their first farm, award the badge
            badge_name = "First Farm"
            badge = db.exec(select(Badge).where(Badge.name == badge_name)).first()
            
            if badge:
                # Check if they already have it (e.g., from testing)
                existing_link = db.get(UserBadge, (current_user.id, badge.id))
                if not existing_link:
                    new_badge_link = UserBadge(user_id=current_user.id, badge_id=badge.id)
                    db.add(new_badge_link)
                    db.commit() # Commit the new badge link
    except Exception as e:
        # If badge logic fails, just log it but don't crash the farm creation
        print(f"Error awarding 'First Farm' badge: {e}")
    # --- ^^^^ END NEW BADGE LOGIC ^^^^ ---

    return db_farm


@router.get("/", response_model=List[FarmRead])
def read_farms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farms = db.exec(select(Farm).where(Farm.owner_id == current_user.id)).all()
    return farms


@router.get("/{farm_id}", response_model=FarmRead)
def read_farm(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return farm


@router.patch("/{farm_id}", response_model=FarmRead)
async def update_farm(farm_id: int, farm_update: FarmCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_farm = db.get(Farm, farm_id)
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if db_farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    farm_data = farm_update.model_dump(exclude_unset=True)

    if 'location_text' in farm_data and farm_data['location_text'] != db_farm.location_text:
        coords = await get_coords_from_location(farm_data['location_text'])
        if not coords:
            raise HTTPException(
                status_code=4.04, detail=f"Could not find new coordinates")
        farm_data.update(coords)

    for key, value in farm_data.items():
        setattr(db_farm, key, value)

    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(farm_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(farm)
    db.commit()
    return