from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .. import models, database

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

# Modele danych dla requestów
class AnalysisRequest(BaseModel):
    text: str
    previous_context: str = ""

class DateRange(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. Analiza pojedynczego wpisu ---
@router.post("/analyze_mood")
async def analyze_mood(request: AnalysisRequest):
    simulated_response = (
        f"Otrzymałem Twój wpis: '{request.text}'. "
        "Jako Twój asystent AI widzę, że czujesz się [TUTAJ BĘDZIE ANALIZA]. "
        "Sugeruję krótki spacer."
    )
    return {"analysis": simulated_response}

# --- 2. Analiza tygodniowa (TEN ENDPOINT JEST KLUCZOWY) ---
@router.post("/weekly_summary/{user_id}")
async def analyze_weekly_summary(
    user_id: int, 
    date_range: DateRange = None, 
    db: Session = Depends(get_db)
):
    # Domyślnie ostatnie 7 dni
    if date_range is None or not date_range.end_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
    else:
        start_date = date_range.start_date
        end_date = date_range.end_date

    # Pobieramy wpisy
    entries = db.query(models.MoodEntry).filter(
        and_(
            models.MoodEntry.owner_id == user_id,
            models.MoodEntry.date >= start_date,
            models.MoodEntry.date <= end_date
        )
    ).all()

    # Jeśli brak wpisów
    if not entries:
        return {
            "entry_count": 0,
            "average_mood_rating": 0.0,
            "mood_stats": {},
            "ai_suggestion": "Brak danych z tego okresu. Dodaj więcej wpisów!"
        }

    # Statystyka
    stats: Dict[str, int] = {}
    mood_rating_sum = 0.0
    
    for entry in entries:
        cat = entry.category
        stats[cat] = stats.get(cat, 0) + 1
        mood_rating_sum += entry.mood_rating

    average_mood = mood_rating_sum / len(entries) if entries else 0
    
    # Symulacja porady AI
    summary_text = ", ".join([f"{count}x {mood}" for mood, count in stats.items()])
    ai_advice = (
        f"W tym okresie dominowały: {summary_text}. "
        f"Średnia nastroju: {round(average_mood, 1)}/5.0. "
        "Wygląda na to, że masz zróżnicowany czas. Pamiętaj o odpoczynku!"
    )

    return {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "entry_count": len(entries),
        "average_mood_rating": round(average_mood, 2),
        "mood_stats": stats,
        "ai_suggestion": ai_advice
    }