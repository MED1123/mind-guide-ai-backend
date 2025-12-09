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

@router.post("/analyze_mood")
async def analyze_mood(request: AnalysisRequest):
    simulated_response = (
        f"Otrzymałem Twój wpis: '{request.text}'. "
        "Jako Twój asystent AI widzę, że czujesz się [TUTAJ BĘDZIE ANALIZA]. "
        "Sugeruję krótki spacer."
    )
    return {"analysis": simulated_response}

# --- ANALIZA TYGODNIOWA (ZMODYFIKOWANA) ---
@router.post("/weekly_summary/{user_id}")
async def analyze_weekly_summary(
    user_id: int, 
    date_range: DateRange = None, 
    db: Session = Depends(get_db)
):
    # Domyślnie ostatnie 7 dni
    if date_range is None or not date_range.end_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6) # 7 dni wliczając dzisiaj
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

    # --- NOWA LOGIKA: DZIENNY ROZKŁAD WPISÓW ---
    # Inicjalizujemy mapę zerami dla każdego dnia w zakresie
    daily_counts: Dict[str, int] = {}
    delta = (end_date - start_date).days + 1
    
    # Tworzymy klucze dat (np. "2023-12-01") dla całego zakresu
    for i in range(delta):
        day = start_date + timedelta(days=i)
        key = day.strftime('%Y-%m-%d')
        daily_counts[key] = 0

    # Statystyka Nastrojów
    stats: Dict[str, int] = {}
    mood_rating_sum = 0.0
    
    for entry in entries:
        # 1. Zliczanie nastrojów
        cat = entry.category
        stats[cat] = stats.get(cat, 0) + 1
        mood_rating_sum += entry.mood_rating
        
        # 2. Zliczanie dzienne (Wykres Czas - Ilość)
        entry_day_key = entry.date.strftime('%Y-%m-%d')
        if entry_day_key in daily_counts:
            daily_counts[entry_day_key] += 1

    average_mood = mood_rating_sum / len(entries) if entries else 0
    
    # Symulacja porady AI
    if not entries:
        ai_advice = "Brak danych z tego okresu. Dodaj wpisy, abym mógł przygotować wykres i analizę."
    else:
        summary_text = ", ".join([f"{count}x {mood}" for mood, count in stats.items()])
        trend = "stabilny"
        if average_mood > 4.0: trend = "bardzo pozytywny"
        elif average_mood < 2.5: trend = "wymagający uwagi"
        
        ai_advice = (
            f"W tym okresie Twój nastrój był {trend}. "
            f"Dominowały: {summary_text}. "
            f"Średnia ocena: {round(average_mood, 1)}/5.0. "
            "Na podstawie wykresu widzę, że byłeś aktywny. "
            "Jeśli czujesz zmęczenie, pamiętaj o regeneracji w weekend."
        )

    return {
        "period": {
            "start": start_date,
            "end": end_date
        },
        "entry_count": len(entries),
        "average_mood_rating": round(average_mood, 2),
        "mood_stats": stats,
        "daily_counts": daily_counts, # <--- TO JEST NOWE DLA WYKRESU
        "ai_suggestion": ai_advice
    }