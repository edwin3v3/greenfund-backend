# GreenFund-test-Backend-backup/app/soil_model.py
import os
import json
import base64
from openai import OpenAI, APIError # Import OpenAI and potential error types
from typing import Dict, Any
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Reusable OpenAI Client Function ---
def get_openai_client():
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured.")
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Optional: Test the connection immediately (costs a tiny amount)
        # client.models.list()
        return client
    except APIError as e:
         # Handle potential authentication errors during client creation
         print(f"OpenAI API Error during client creation: {e}")
         raise HTTPException(status_code=500, detail=f"OpenAI client initialization failed: {e}")
    except Exception as e:
         print(f"Unexpected error during OpenAI client creation: {e}")
         raise HTTPException(status_code=500, detail=f"Unexpected error initializing OpenAI client.")


async def analyze_soil_with_ai(data: Dict[str, float]) -> Dict[str, Any]:
    """Analyzes soil data from manual text input using OpenAI."""
    client = get_openai_client()
    prompt = f"""
    Analyze the following soil data for a farm in Kenya:
    - pH: {data['ph']}, Nitrogen (N): {data['nitrogen']} ppm, Phosphorus (P): {data['phosphorus']} ppm, Potassium (K): {data['potassium']} ppm, Moisture: {data['moisture']}%
    Provide a concise analysis of the soil's health and a list of suitable crops.
    Return ONLY a valid JSON object (no extra text or markdown) with keys "ai_analysis_text" (string) and "suggested_crops" (list of strings).
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini", # Use a capable OpenAI model
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert Kenyan agronomist providing advice."},
                {"role": "user", "content": prompt}
            ]
        )
        response_content = completion.choices[0].message.content
        return json.loads(response_content)
    except APIError as e:
        # Handle specific OpenAI errors during the call
        print(f"OpenAI API Error during soil analysis: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=f"AI analysis failed: {e.message}")
    except Exception as e:
        print(f"Error calling OpenAI for manual soil analysis: {e}")
        # Use a generic 500 for other unexpected errors
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {e}")


async def analyze_soil_image_with_ai(image_data: bytes) -> Dict[str, Any]:
    """Analyzes a soil image using OpenAI's multi-modal capabilities."""
    client = get_openai_client()
    base64_image = base64.b64encode(image_data).decode('utf-8')

    prompt_messages = [
        {
            "role": "system",
            "content": "You are an expert soil scientist specializing in Kenyan agriculture analyzing a soil image."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """
                    Based on the attached soil image from a Kenyan farm:
                    1. Identify the likely soil type (e.g., Clay, Loam, Sandy, Red Lateritic, Black Cotton Soil).
                    2. Analyze its probable characteristics (drainage, water retention, fertility).
                    3. Suggest suitable crops for this soil type in Kenya.

                    Return ONLY a valid JSON object (no extra text or markdown) with two keys:
                    - "ai_analysis_text": String with identification and analysis.
                    - "suggested_crops": JSON list of crop names.
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]

    try:
        completion = client.chat.completions.create(
            # Ensure you use a model that supports vision, like gpt-4o or gpt-4-turbo
            model="gpt-4o-mini",
            messages=prompt_messages,
            # If JSON output fails with vision, remove response_format and rely on prompt
            response_format={"type": "json_object"},
        )
        response_content = completion.choices[0].message.content
        ai_data = json.loads(response_content)

        ai_data.update({"ph": 0.0, "nitrogen": 0, "phosphorus": 0, "potassium": 0, "moisture": 0})
        return ai_data
    except APIError as e:
        print(f"OpenAI API Error during image analysis: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=f"AI image analysis failed: {e.message}")
    except Exception as e:
        print(f"Error calling OpenAI for image analysis: {e}")
        raise HTTPException(status_code=500, detail=f"AI image analysis failed: {e}")