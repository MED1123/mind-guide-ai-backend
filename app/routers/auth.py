from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .. import models, schemas, database
from pydantic import BaseModel
import uuid
# We no longer use local passlib hashing
# from passlib.context import CryptContext 
# from ..services.email_service import EmailService # Optional if Supabase handles emails

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- REJESTRACJA ---
@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Register with Supabase Auth
    try:
        # This triggers Supabase validation (email unique, etc.) and sending confirmation email
        auth_response = database.supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "username": user.username
                }
            }
        })
    except Exception as e:
        # Parse Supabase error
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Check if user actually created (or if verify required)
    if not auth_response.user:
        raise HTTPException(status_code=400, detail="Registration failed")
    
    user_id_uuid = uuid.UUID(auth_response.user.id)

    # 3. Create Local Profile in public.users
    # Check if exists first (idempotency)
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        # Could happen if auth user created but profile failed previously
        return db_user

    new_user = models.User(
        id=user_id_uuid, # Sync ID with Supabase Auth
        email=user.email,
        username=user.username,
        is_active=True,
        is_verified=False # Supabase manages this, but we store status. 
                          # Ideally we check auth.users.email_confirmed_at via API or trigger.
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        print(f"DEBUG: Profile creation failed: {e}") # Debugging
        db.rollback()
        # If profile creation fails, we technically have an orphaned auth user.
        # But usually we return error.
        raise HTTPException(status_code=500, detail=f"Profile creation failed: {str(e)}")
    
    # We rely on Supabase to send the email now.
    # If using custom SMTP service via code instead of Supabase SMTP:
    # EmailService.send_verification_email(...) 
    
    return new_user

# --- LOGOWANIE ---
class LoginResponse(BaseModel):
    user_id: str # UUID string
    email: str
    access_token: str
    message: str

@router.post("/login", response_model=LoginResponse)
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Sign in with Supabase
    try:
        auth_response = database.supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not auth_response.user or not auth_response.session:
        raise HTTPException(status_code=400, detail="Login failed")

    # 2. Check Profile in Local DB
    db_user = db.query(models.User).filter(models.User.id == uuid.UUID(auth_response.user.id)).first()
    
    if not db_user:
        # Create profile if missing (resilience)
        db_user = models.User(
            id=uuid.UUID(auth_response.user.id),
            email=user.email,
            username=user.username or "",
            is_active=True
        )
        db.add(db_user)
        db.commit()
    
    # 3. Return Token (Supabase JWT)
    return {
        "user_id": str(db_user.id),
        "email": db_user.email,
        "access_token": auth_response.session.access_token,
        "message": "Zalogowano pomyślnie"
    }

# --- RESET HASŁA ---
@router.post("/forgot-password")
async def forgot_password(email: str = Form(...)):
    try:
        database.supabase.auth.reset_password_for_email(email)
        return {"message": "Password reset link sent (if email exists)."}
    except Exception as e:
        # Don't leak exists status errors if possible, but simpler logging here
        print(e)
        return {"message": "Password reset link sent (if email exists)."}

# Note: /reset-password-confirm usually handled by Frontend with the link from email
# which redirects to app with #access_token=..., then app calls update_user.