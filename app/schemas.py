from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- MOOD ENTRY SCHEMAS ---

# To przesyła Flutter przy tworzeniu wpisu
class MoodEntryCreate(BaseModel):
    text: str
    mood_rating: float
    category: str
    image_paths: List[str] = [] # Na razie jako lista stringów

# To zwraca API (dodajemy ID i datę utworzenia)
class MoodEntry(MoodEntryCreate):
    id: int
    date: datetime
    owner_id: int

    class Config:
        from_attributes = True

# --- USER SCHEMAS ---

# To przesyła Flutter przy rejestracji
class UserCreate(BaseModel):
    email: str
    password: str

# To zwraca API (nie zwracamy hasła!)
class User(BaseModel):
    id: int
    email: str
    is_active: bool
    entries: List[MoodEntry] = []

    class Config:
        from_attributes = True