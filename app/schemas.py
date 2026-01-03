from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
import uuid

# --- MOOD ENTRY SCHEMAS ---

class MoodEntryCreate(BaseModel):
    text: str
    mood_rating: float
    category: str
    image_paths: List[str] = []
    date: Optional[datetime] = None
    conversation: Optional[str] = ""
    ai_analysis: Optional[str] = ""

class MoodEntry(MoodEntryCreate):
    id: int # MoodEntry ID remains int in DB for now (unless we migrated it too, but SQL script didn't invalid it)
            # Actually, the SQL script didn't change mood_entries.id type, only added user_id. 
            # Ideally keys should be consistent, but let's respect existing DB structure for now.
    date: datetime
    ai_analysis: str = ""
    conversation: str = ""
    owner_id: uuid.UUID # Changed to UUID

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
    custom_assistant_name: Optional[str] = None # Added field
    password: Optional[str] = None # Used for password change manually if custom auth
    old_password: Optional[str] = None

class User(BaseModel):
    id: uuid.UUID
    email: str
    username: Optional[str] = None
    is_active: bool
    is_verified: bool = False
    name: str = ""
    surname: str = ""
    username: str = ""
    birth_date: str = ""
    profile_image_path: str = ""
    is_dark_mode: bool = False
    custom_assistant_name: str = "" # Added field
    entries: List[MoodEntry] = []

    class Config:
        from_attributes = True