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

# Dodawanie wpisu dla konkretnego użytkownika (uproszczone)
@router.post("/{user_id}", response_model=schemas.MoodEntry)
def create_entry_for_user(
    user_id: int, 
    entry: schemas.MoodEntryCreate, 
    db: Session = Depends(get_db)
):
    # Tworzymy model bazy danych z danych Pydantic
    # image_paths na razie pomijamy lub konwertujemy na string, jeśli baza tego wymaga
    db_entry = models.MoodEntry(
        **entry.dict(exclude={"image_paths"}), 
        owner_id=user_id
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

# Pobieranie wszystkich wpisów
@router.get("/", response_model=List[schemas.MoodEntry])
def read_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    entries = db.query(models.MoodEntry).offset(skip).limit(limit).all()
    return entries