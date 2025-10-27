import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, desc
from typing import Dict, Any # Added Dict, Any

from app.database import get_db
from app.models import Farm, User, FarmActivity
from app.security import get_current_user
from app.recommendations import generate_recommendations # Keep using this

router = APIRouter(prefix="/climate", tags=["Climate"])

# Use the same helper function for consistency
async def _fetch_weather_data(latitude: float, longitude: float, daily_params: str) -> Dict[str, Any]:
    """Fetches weather data from Open-Meteo."""
    WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": latitude, "longitude": longitude, "daily": daily_params, "timezone": "auto"}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(WEATHER_API_URL, params=params, timeout=10.0)
            response.raise_for_status()
            # Return the full forecast structure, not just daily
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"ERROR: Open-Meteo API returned status {e.response.status_code}: {e.response.text}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Weather service returned an error.")
    except httpx.RequestError as e:
        print(f"ERROR: Could not connect to Open-Meteo API: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not connect to the weather service.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while fetching weather data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


@router.get("/{farm_id}/forecast")
async def get_weather_forecast_and_recommendations( # Renamed function for clarity
    farm_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    if farm.owner_id != current_user.id: # Ensure ownership check
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this farm")

    activities = db.exec(
        select(FarmActivity)
        .where(FarmActivity.farm_id == farm_id)
        .order_by(desc(FarmActivity.date))
        .limit(5) # Only need recent activities for recommendations
    ).all()

    # --- Fetch ALL necessary weather params for rules ---
    weather_params = (
        "weathercode,temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,relative_humidity_2m_mean,et0_fao_evapotranspiration" # Added humidity and ET
    )
    # --- END ---

    try:
        full_forecast_data = await _fetch_weather_data(farm.latitude, farm.longitude, weather_params)
        daily_data = full_forecast_data.get("daily", {})

        # Call the updated recommendation function
        recommendations = await generate_recommendations(
            daily_data, # Pass only the daily part to recommendations
            activities,
            farm.current_crop
        )

        return {
            # Return the full forecast for potential frontend use
            "forecast": full_forecast_data,
            "recommendations": recommendations
        }

    except HTTPException as http_exc:
         # Re-raise HTTP exceptions from weather fetch or AI call
         raise http_exc
    except Exception as e:
        # Catch unexpected errors during processing
        print(f"ERROR generating forecast/recommendations response: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred generating recommendations: {e}")