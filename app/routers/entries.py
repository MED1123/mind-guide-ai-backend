from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime # <--- WAŻNY NOWY IMPORT
from .. import models, schemas, database

router = APIRouter(
    prefix="/entries",
    tags=["entries"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dodawanie wpisu
@router.post("/{user_id}", response_model=schemas.MoodEntry)
def create_entry_for_user(
    user_id: int, 
    entry: schemas.MoodEntryCreate, 
    db: Session = Depends(get_db)
):
    # 1. Logika Daty:
    # Jeśli frontend przysłał datę (np. z generatora testowego), używamy jej.
    # Jeśli nie (entry.date jest None), używamy aktualnego czasu.
    final_date = entry.date if entry.date else datetime.now()

    # 2. Obsługa zdjęć:
    # Konwersja listy zdjęć na string (np. "img1.jpg|img2.jpg") do zapisu w bazie
    images_str = "|".join(entry.image_paths) if entry.image_paths else ""

    # 3. Tworzenie obiektu bazy danych
    db_entry = models.MoodEntry(
        date=final_date,          # <--- TUTAJ PRZEKAZUJEMY DATĘ
        text=entry.text,
        mood_rating=entry.mood_rating,
        category=entry.category,
        image_paths=images_str, 
        owner_id=user_id,
        # Pola domyślne wymagane przez model (jeśli nie ma ich w schemas.create)
        ai_analysis="",
        conversation=""
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    # 4. Przygotowanie odpowiedzi:
    # Musimy ręcznie skonstruować obiekt odpowiedzi, aby upewnić się, 
    # że 'image_paths' wraca jako lista, a nie string z bazy.
    return schemas.MoodEntry(
        id=db_entry.id,
        date=db_entry.date,
        text=db_entry.text,
        mood_rating=db_entry.mood_rating,
        category=db_entry.category,
        ai_analysis=db_entry.ai_analysis,
        conversation=db_entry.conversation,
        # Konwersja stringa "a|b" na listę ["a", "b"]
        image_paths=db_entry.image_paths.split("|") if db_entry.image_paths else [],
        owner_id=db_entry.owner_id
    )

@router.get("/{user_id}", response_model=List[schemas.MoodEntry])
def read_entries(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Filtrujemy po owner_id == user_id
    entries = db.query(models.MoodEntry)\
        .filter(models.MoodEntry.owner_id == user_id)\
        .order_by(models.MoodEntry.date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Konwersja stringa z bazy z powrotem na listę dla każdego wpisu
    # (Pydantic oczekuje listy, baza zwraca string)
    results = []
    for entry in entries:
        # Tworzymy obiekt schematu ręcznie lub modyfikujemy obiekt SQLAlchemy
        # Najbezpieczniej jest zmapować to na schema:
        img_list = entry.image_paths.split("|") if entry.image_paths else []
        
        results.append(schemas.MoodEntry(
            id=entry.id,
            date=entry.date,
            text=entry.text,
            mood_rating=entry.mood_rating,
            category=entry.category,
            ai_analysis=entry.ai_analysis,
            conversation=entry.conversation,
            image_paths=img_list,
            owner_id=entry.owner_id
        ))
            
    return results