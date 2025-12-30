from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    name = Column(String, default="")
    surname = Column(String, default="")
    username = Column(String, default="")
    birth_date = Column(String, default="")
    profile_image_path = Column(String, default="")
    
    # Relacja: Jeden użytkownik ma wiele wpisów
    entries = relationship("MoodEntry", back_populates="owner")

class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    mood_rating = Column(Float) # Używamy Float dla oceny 1.0 - 5.0
    category = Column(String)
    
    # Nowe pola do synchronizacji
    ai_analysis = Column(String, default="")
    conversation = Column(String, default="")
    image_paths = Column(String, default="") # Będziemy tu trzymać ścieżki oddzielone "|"
    
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Klucz obcy
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="entries")

class AiAnalysisCache(Base):
    __tablename__ = "ai_analysis_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    range_type = Column(String) # Dzień, Tydzień, Miesiąc, Rok
    ai_suggestion = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())