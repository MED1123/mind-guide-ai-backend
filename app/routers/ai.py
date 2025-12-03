from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

class AnalysisRequest(BaseModel):
    text: str
    previous_context: str = ""

@router.post("/analyze_mood")
async def analyze_mood(request: AnalysisRequest):
    """
    To jest miejsce, gdzie w przyszłości podłączymy OpenAI lub Anthropic.
    Na razie zwracamy symulowaną odpowiedź, żeby Flutter miał co odebrać.
    """
    
    # Tu będzie: response = openai.ChatCompletion.create(...)
    
    simulated_response = (
        f"Otrzymałem Twój wpis: '{request.text}'. "
        "Jako Twój asystent AI widzę, że czujesz się [TUTAJ BĘDZIE ANALIZA]. "
        "Sugeruję krótki spacer."
    )
    
    return {"analysis": simulated_response}