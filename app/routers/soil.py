from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session, select, desc, func
from typing import List

from app.database import get_db
from app.models import Farm, SoilReport, User, Badge, UserBadge
# <-- Import the new schema
from app.schemas import SoilReportCreate, SoilReportRead, CropSuggestionSummaryResponse
from app.security import get_current_user
from app.soil_model import analyze_soil_with_ai, analyze_soil_image_with_ai

router = APIRouter(prefix="/soil", tags=["Soil"])

# --- Badge Logic ---
def _award_soil_badge(db: Session, current_user: User):
    try:
        user_farm_ids_query = select(Farm.id).where(Farm.owner_id == current_user.id)
        report_count = db.exec(
            select(func.count(SoilReport.id))
            .where(SoilReport.farm_id.in_(user_farm_ids_query))
        ).one()

        if report_count == 1:
            badge_name = "Soil Analyst"
            badge = db.exec(select(Badge).where(Badge.name == badge_name)).first()
            if badge:
                existing_link = db.get(UserBadge, (current_user.id, badge.id))
                if not existing_link:
                    new_badge_link = UserBadge(user_id=current_user.id, badge_id=badge.id)
                    db.add(new_badge_link)
                    db.commit()
    except Exception as e:
        print(f"Error awarding 'Soil Analyst' badge: {e}")
# --- End Badge Logic ---


@router.post("/manual", response_model=SoilReportRead, status_code=status.HTTP_201_CREATED)
async def create_soil_report_manual(
    report_data: SoilReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.get(Farm, report_data.farm_id)
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found or not owned by user")

    try:
        ai_analysis_data = await analyze_soil_with_ai(report_data.model_dump())
        full_report_data = report_data.model_dump()
        full_report_data.update(ai_analysis_data)
        db_report = SoilReport.model_validate(full_report_data)
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI analysis failed: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save soil report: {e}")

    _award_soil_badge(db, current_user)
    return db_report


@router.post("/upload_soil_image/{farm_id}", response_model=SoilReportRead, status_code=status.HTTP_201_CREATED)
async def upload_soil_image_analysis(
    farm_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.get(Farm, farm_id)
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found or not owned by user")

    if not file.content_type.startswith("image/"):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Please upload an image.")

    try:
        image_data = await file.read()
        ai_analysis_data = await analyze_soil_image_with_ai(image_data)
        full_report_data = {
            "farm_id": farm_id,
            "ph": ai_analysis_data.get("ph", 0.0),
            "nitrogen": ai_analysis_data.get("nitrogen", 0),
            "phosphorus": ai_analysis_data.get("phosphorus", 0),
            "potassium": ai_analysis_data.get("potassium", 0),
            "moisture": ai_analysis_data.get("moisture", 0),
            "ai_analysis_text": ai_analysis_data.get("ai_analysis_text"),
            "suggested_crops": ai_analysis_data.get("suggested_crops"),
        }
        db_report = SoilReport.model_validate(full_report_data)
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
    except ValueError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI image analysis failed: {e}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not process image or save report: {e}")

    _award_soil_badge(db, current_user)
    return db_report


@router.get("/farm/{farm_id}", response_model=List[SoilReportRead])
def get_soil_reports_for_farm(
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.get(Farm, farm_id)
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found or not owned by user")

    reports = db.exec(
        select(SoilReport)
        .where(SoilReport.farm_id == farm_id)
        .order_by(desc(SoilReport.date))
    ).all()
    return reports

# --- vvvv ADD THIS NEW ENDPOINT vvvv ---
@router.get("/suggestions/summary", response_model=CropSuggestionSummaryResponse)
def get_crop_suggestion_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Gets a summary of unique AI crop suggestions from the latest reports
    for all of the user's farms.
    """
    user_farm_ids = db.exec(
        select(Farm.id).where(Farm.owner_id == current_user.id)
    ).all()

    if not user_farm_ids:
        return CropSuggestionSummaryResponse(unique_suggestion_count=0, recent_suggestions=[])

    # Subquery to find the latest report ID per farm (that has suggestions)
    latest_report_ids_subquery = (
        select(func.max(SoilReport.id))
        .where(SoilReport.farm_id.in_(user_farm_ids))
        .where(SoilReport.suggested_crops != None) # Only consider reports that HAVE suggestions
        .group_by(SoilReport.farm_id)
    ).scalar_subquery()

    # Fetch the actual reports using the IDs
    latest_reports = db.exec(
        select(SoilReport)
        .where(SoilReport.id.in_(latest_report_ids_subquery))
        .order_by(desc(SoilReport.date)) # Order by date to get most recent first
    ).all()

    # Collect unique suggestions, keeping track of recency
    unique_suggestions = set()
    all_suggestions_ordered = [] # Keep order
    for report in latest_reports:
        if report.suggested_crops: # Should always be true based on subquery, but good check
            for crop in report.suggested_crops:
                 if crop not in unique_suggestions:
                     all_suggestions_ordered.append(crop)
                     unique_suggestions.add(crop)

    # Get the top 3 most recent unique suggestions
    recent_unique = all_suggestions_ordered[:3]

    return CropSuggestionSummaryResponse(
        unique_suggestion_count=len(unique_suggestions),
        recent_suggestions=recent_unique
    )
# --- ^^^^ END NEW ENDPOINT ^^^^ ---