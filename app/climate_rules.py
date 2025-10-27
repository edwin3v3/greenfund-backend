from typing import Dict, List, Any
from app.models import FarmActivity

def assess_pest_disease_risks(daily_forecast: Dict[str, Any], current_crop: str = None) -> Dict[str, str]:
    """Simple rule-based assessment of pest/disease risks based on weather."""
    risks = {}
    temps_max = daily_forecast.get("temperature_2m_max", [])
    temps_min = daily_forecast.get("temperature_2m_min", [])
    precip = daily_forecast.get("precipitation_sum", [])
    humidity = daily_forecast.get("relative_humidity_2m_mean", []) # Assuming this is fetched

    avg_temp = sum(temps_max) / len(temps_max) if temps_max else 20
    total_precip = sum(precip) if precip else 0
    avg_humidity = sum(humidity) / len(humidity) if humidity else 60

    # Rule 1: Powdery Mildew (High Humidity)
    high_humidity_days = sum(1 for h in humidity if h > 85)
    if high_humidity_days >= 3 and avg_humidity > 75:
        risks["Powdery Mildew"] = "High"
    elif high_humidity_days >= 1 or avg_humidity > 70:
         risks["Powdery Mildew"] = "Medium"

    # Rule 2: Aphids / Fall Armyworm (Warm and Dryish)
    warm_days = sum(1 for t_max in temps_max if t_max > 28) # Example threshold
    dry_period = total_precip < 10 # Example threshold (less than 10mm total rain)
    if warm_days >= 3 and dry_period:
        risks["Aphids"] = "Medium"
        risks["Fall Armyworm"] = "Medium"
    elif warm_days >= 1 and dry_period:
        risks["Aphids"] = "Low"
        # Fall Armyworm might need slightly different conditions, keep simple for now
        # risks["Fall Armyworm"] = "Low"

    # Add more rules based on crop, specific temp ranges, etc.

    # Limit to top 2 risks for simplicity in the prompt
    sorted_risks = sorted(risks.items(), key=lambda item: {"High": 3, "Medium": 2, "Low": 1}.get(item[1], 0), reverse=True)
    return dict(sorted_risks[:2])


def assess_water_stress(daily_forecast: Dict[str, Any]) -> str:
    """Simple rule-based assessment of water stress."""
    precip = daily_forecast.get("precipitation_sum", [])
    et0 = daily_forecast.get("et0_fao_evapotranspiration", []) # Correct ET param

    if not precip or not et0 or len(precip) != len(et0):
        return "Unknown" # Cannot assess if data is missing

    net_water = sum(p - e for p, e in zip(precip, et0))

    if net_water < -20: # Significant water loss
        return "High"
    elif net_water < -5: # Moderate water loss
        return "Medium"
    elif net_water < 5: # Minor loss or small gain
        return "Low"
    else: # Significant gain
        return "Very Low / Surplus"


def assess_carbon_trend(activities: List[FarmActivity]) -> str:
    """Placeholder assessment of carbon trend based on recent activities."""
    # This needs more robust logic or data in a real application
    activity_types = [a.activity_type for a in activities[:5]] # Look at last 5
    
    # Basic check - this is very simplified
    if "Fertilizing" in activity_types:
        # Assuming conventional fertilizer increases emissions short-term
        return "Potential Increase (Fertilizing)"
    # Add checks for positive actions like planting cover crops if logged
    # elif "Planting Cover Crop" in activity_types:
    #     return "Potential Improvement (Cover Crop)"
    else:
        return "Likely Stable / Unknown"