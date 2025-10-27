# GreenFund-test-Backend-backup/app/routers/chatbot.py
from fastapi import APIRouter
from pydantic import BaseModel
from openai import APIError # Import error type
from app.soil_model import get_openai_client # Import the correct client function

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    prompt: str

def get_chatbot_system_prompt() -> str:
    return """
    You are GreenBot, a friendly and knowledgeable AI assistant for Kenyan smallholder farmers.
    Your goal is to provide helpful, concise, and practical advice on sustainable farming and climate action.
    Answer questions related to: soil health, pest control, crop selection, water management, and reducing carbon footprint.
    Do NOT answer questions outside of this scope (e.g., politics, general knowledge).
    Keep your answers encouraging and easy to understand.
    """

@router.post("/ask")
async def ask_chatbot(request: ChatRequest):
    try:
        client = get_openai_client()
        completion = client.chat.completions.create(
            model="gpt-4o-mini", # Use a standard chat model
            messages=[
                {"role": "system", "content": get_chatbot_system_prompt()},
                {"role": "user", "content": request.prompt}
            ]
        )
        response_content = completion.choices[0].message.content
        return {"reply": response_content}
    except APIError as e:
        print(f"OpenAI API Error during chatbot request: {e}")
        raise HTTPException(status_code=e.status_code or 500, detail=f"AI chatbot failed: {e.message}")
    except Exception as e:
        print(f"Error calling OpenAI for chatbot: {e}")
        # Use a generic error message for the user in case of failure
        raise HTTPException(status_code=500, detail="Sorry, the chatbot encountered an error. Please try again later.")