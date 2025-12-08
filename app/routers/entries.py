from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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
    # Konwersja listy zdjęć na string (np. "img1.jpg|img2.jpg")
    # Dzięki temu zapiszemy to w jednej kolumnie w bazie
    images_str = "|".join(entry.image_paths) if entry.image_paths else ""

    db_entry = models.MoodEntry(
        text=entry.text,
        mood_rating=entry.mood_rating,
        category=entry.category,
        image_paths=images_str, 
        owner_id=user_id
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    # Ważne: Przed zwróceniem odpowiedzi musimy "oszukać" Pydantic
    # i przypisać z powrotem listę, bo tego oczekuje aplikacja
    db_entry.image_paths = entry.image_paths
    return db_entry

# Pobieranie wpisów
@router.get("/", response_model=List[schemas.MoodEntry])
def read_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entries = db.query(models.MoodEntry).offset(skip).limit(limit).all()
    
    # Konwersja stringa z bazy z powrotem na listę dla każdego wpisu
    for entry in entries:
        if entry.image_paths:
            entry.image_paths = entry.image_paths.split("|")
        else:
            entry.image_paths = []
            
    return entries