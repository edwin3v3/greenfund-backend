# GreenFund-test-Backend-backup/app/carbon_model.py
import json
from typing import Optional
from openai import APIError # Import error type
from app.soil_model import get_openai_client # Import the correct client function

async def estimate_carbon_with_ai(activity_type: str, value: float, unit: str, description: Optional[str]) -> float:
    """Estimates the carbon footprint for a farm activity by asking OpenAI."""
    try:
        client = get_openai_client()
    except HTTPException as e:
        # Handle client init failure (e.g., bad key)
         print(f"WARNING: OpenAI client failed init. Returning placeholder. Error: {e.detail}")
         return {"Planting": 1.5, "Harvesting": 1.8, "Fertilizing": 10.0}.get(activity_type, 0.5)

    prompt = f"""
    You are a carbon footprint analyst for agriculture.
    A farmer in Kenya performed:
    - Activity: {activity_type}
    - Details: {description or 'No description.'}
    - Amount: {value} {unit}

    Consider: "Planting"/"Harvesting" with "litres" implies diesel. "Fertilizing" with "kg" implies nitrogen fertilizer.

    Provide a single, reasonable estimate for the carbon footprint in kilograms of CO2 equivalent (kg CO2e).
    Return ONLY a valid JSON object (no extra text or markdown) containing a single key: "carbon_kg". Example: {{"carbon_kg": 25.5}}
    """

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        ai_response_str = chat_completion.choices[0].message.content
        ai_data = json.loads(ai_response_str)

        carbon_kg = ai_data.get("carbon_kg")
        if carbon_kg is None or not isinstance(carbon_kg, (int, float)):
            print(f"Warning: OpenAI returned invalid format. Response: {ai_data}")
            return 0.5 # Placeholder on bad format

        return float(carbon_kg)
    except APIError as e:
         # Handle quota errors etc.
         print(f"OpenAI API Error during carbon estimation: {e}")
         # Return placeholder if API fails (e.g., quota)
         return {"Planting": 1.5, "Harvesting": 1.8, "Fertilizing": 10.0}.get(activity_type, 0.5)
    except Exception as e:
        print(f"Error calling OpenAI for carbon estimation: {e}")
        return {"Planting": 1.5, "Harvesting": 1.8, "Fertilizing": 10.0}.get(activity_type, 0.5)