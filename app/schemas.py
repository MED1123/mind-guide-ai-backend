from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime

# --- MOOD ENTRY SCHEMAS ---

class MoodEntryCreate(BaseModel):
    text: str
    mood_rating: float
    category: str
    image_paths: List[str] = []
    date: Optional[datetime] = None

class MoodEntry(MoodEntryCreate):
    id: int
    date: datetime
    ai_analysis: str = ""
    conversation: str = ""
    owner_id: int

    class Config:
        from_attributes = True

    @field_validator('image_paths', mode='before')
    @classmethod
    def parse_image_paths(cls, v):
        if isinstance(v, str):
            return v.split("|") if v else []
        return v

# --- USER SCHEMAS ---

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    username: Optional[str] = None
    birth_date: Optional[str] = None
    email: Optional[str] = None
    profile_image_path: Optional[str] = None
    is_dark_mode: Optional[bool] = None
    password: Optional[str] = None

# Tutaj dodaliśmy brakujące pola, żeby API je zwracało po rejestracji
class User(BaseModel):
    id: int
    email: str
    is_active: bool
    name: str = ""
    surname: str = ""
    username: str = ""
    birth_date: str = ""
    profile_image_path: str = ""
    is_dark_mode: bool = False
    entries: List[MoodEntry] = []

    class Config:
        from_attributes = True