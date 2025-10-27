import httpx
from fastapi import HTTPException, status


async def get_coords_from_location(location_text: str):
    """Calls the Nominatim API to get lat/lon for a location name, restricted to Kenya."""
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location_text,
        "format": "json",
        "limit": 1,
        "countrycodes": "ke"
    }
    headers = {"User-Agent": "GreenFundApp/1.0"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(NOMINATIM_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not data:
                return None
            return {
                "latitude": float(data[0]["lat"]),
                "longitude": float(data[0]["lon"]),
            }
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
