import requests
import os
import json

# ... (other imports remain, but making sure they are cleaner)
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
    lang: str = "pl"  # Default to Polish

class DateRange(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    lang: str = "pl" # Support lang in DateRange or pass separately

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze_mood")
async def analyze_mood(request: AnalysisRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    # ... (rest of configuration)

    # Prompt selection
    if request.lang == 'en':
        system_prompt = (
            "You are an empathetic mental health assistant. "
            "Your task is to briefly analyze the user's mood based on their entry. "
            "Respond briefly, warmly, and in English. "
            "Suggest one simple activity that might help."
        )
    else:
        system_prompt = (
            "Jesteś empatycznym asystentem zdrowia psychicznego. "
            "Twoim zadaniem jest krótka analiza nastroju użytkownika na podstawie jego wpisu. "
            "Odpowiadaj krótko, ciepło i po polsku. "
            "Zaproponuj jedną prostą czynność, która może pomóc."
        )

    # ... (rest of payload construction and request)
    # Be careful to use system_prompt variable

# ... (inside analyze_mood function)
    payload = {
        "model": "mistralai/mistral-small-3.1-24b-instruct:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.text}
        ]
    }
# ...

@router.post("/weekly_summary/{user_id}")
async def analyze_weekly_summary(
    user_id: str, 
    date_range: DateRange = None, # Expect lang inside DateRange or body
    db: Session = Depends(get_db)
):
    # Domyślny język
    lang = "pl"
    if date_range and hasattr(date_range, 'lang'):
        lang = date_range.lang

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

    # --- Zaczynamy Cache ---
    # 1. Sprawdzamy czy mamy świeżą analizę w bazie (dla danego usera, zakresu i ostatniej doby)
    range_label = "Custom"
    delta_days = (end_date - start_date).days
    if delta_days <= 1: range_label = "Dzień"
    elif delta_days <= 7: range_label = "Tydzień"
    elif delta_days <= 31: range_label = "Miesiąc"
    elif delta_days >= 360: range_label = "Rok"

    cached_analysis = db.query(models.AiAnalysisCache).filter(
        models.AiAnalysisCache.user_id == user_id,
        models.AiAnalysisCache.range_type == range_label,
        models.AiAnalysisCache.created_at >= datetime.now() - timedelta(hours=24)
    ).order_by(models.AiAnalysisCache.created_at.desc()).first()

    if cached_analysis:
        ai_advice = cached_analysis.ai_suggestion
        print(f"CACHE HIT: Using cached advice for {user_id} ({range_label})")
        # Jeśli cache jest trafiony, nie pytamy AI
    else:
        # ...
        if not entries:
            ai_advice = "No data for this period." if lang == 'en' else "Brak danych z tego okresu."
        else:
             # Construct the prompt
            mood_summary = ", ".join([f"{mood}: {count}" for mood, count in stats.items()])
            
            if lang == 'en':
                prompt_text = (
                    f"Analyze user activity from {start_date.strftime('%d.%m')} to {end_date.strftime('%d.%m')}. "
                    f"Entry count: {len(entries)}. "
                    f"Average mood: {round(average_mood, 1)}/5.0. "
                    f"Mood distribution: {mood_summary}. "
                    "Based on this data, write a short, personalized opinion (max 2 sentences). "
                    "Address the user directly. "
                    "Suggest a concrete advice or observation."
                )
                system_prompt_weekly = "You are an empathetic psychologist and data analyst. Your goal is to draw conclusions from the user's mood. Write briefly and in English."
            else:
                prompt_text = (
                    f"Przeanalizuj aktywność użytkownika z okresu {start_date.strftime('%d.%m')} - {end_date.strftime('%d.%m')}. "
                    f"Liczba wpisów: {len(entries)}. "
                    f"Średnia ocena nastroju: {round(average_mood, 1)}/5.0. "
                    f"Rozkład nastrojów: {mood_summary}. "
                    "Na podstawie tych danych napisz krótką, spersonalizowaną opinię (max 2 zdania). "
                    "Zwróć się bezpośrednio do użytkownika. "
                    "Zaproponuj konkretną radę lub obserwację (np. 'Zalecam więcej snu, ponieważ...')."
                )
                system_prompt_weekly = "Jesteś empatycznym psychologiem i analitykiem danych. Twoim celem jest wyciągnięcie wniosków z nastroju użytkownika. Pisz krótko i po polsku."

            # Call AI with Fallback
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                ai_advice = "Błąd: Brak klucza API do analizy."
            else:
                models_to_try = [
                    "mistralai/mistral-small-3.1-24b-instruct:free",
                    "google/gemini-2.0-flash-exp:free",
                    "meta-llama/llama-3.2-11b-vision-instruct:free",
                    "microsoft/phi-3-mini-128k-instruct:free"
                ]
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://mindguide.app",
                    "X-Title": "Mind Guide AI"
                }
                
                ai_advice = "Nie udało się wygenerować analizy (wszystkie modele zajęte)."
                
                for model in models_to_try:
                    try:
                        payload = {
                            "model": model,
                            "messages": [
                                {
                                    "role": "system", 
                                    "content": system_prompt_weekly
                                },
                                {"role": "user", "content": prompt_text}
                            ]
                        }
                        
                        print(f"Trying model: {model}")
                        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=15)
                        
                        if resp.status_code == 200:
                            data = resp.json()
                            if 'choices' in data and len(data['choices']) > 0:
                                ai_advice = data['choices'][0]['message']['content']
                                # Zapisujemy do Cache
                                new_cache = models.AiAnalysisCache(
                                    user_id=user_id,
                                    range_type=range_label,
                                    ai_suggestion=ai_advice
                                )
                                db.add(new_cache)
                                db.commit()
                                break # Success!
                        else:
                            print(f"Model {model} failed: {resp.status_code} - {resp.text}")
                            
                    except Exception as e:
                        print(f"Exception dealing with {model}: {e}")
                        continue

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