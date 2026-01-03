from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    # User ID is now a UUID matching auth.users
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile fields only - no auth secrets
    name = Column(String, default="")
    surname = Column(String, default="")
    username = Column(String, default="")
    birth_date = Column(String, default="")
    profile_image_path = Column(String, default="")
    is_dark_mode = Column(Boolean, default=False)
    custom_assistant_name = Column(String, default="") # New field for custom AI name
    
    entries = relationship("MoodEntry", back_populates="owner")

class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    
    # We use owner_id pointing to public.users (which shares ID with auth.users)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id")) 
    
    text = Column(String)
    mood_rating = Column(Float)
    category = Column(String)
    
    ai_analysis = Column(String, default="")
    conversation = Column(String, default="")
    image_paths = Column(String, default="")
    
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="entries")

class AiAnalysisCache(Base):
    __tablename__ = "ai_analysis_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    range_type = Column(String)
    ai_suggestion = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SobrietyClock(Base):
    __tablename__ = "sobriety_clocks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    addiction_type = Column(String)
    custom_name = Column(String, default="")
    start_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())