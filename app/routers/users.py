from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import uuid
from ..services.email_service import EmailService
from .. import models, schemas, database

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}", response_model=schemas.User)
def read_user_profile(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
def update_user_profile(user_id: str, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Aktualizacja pól tekstowych
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.surname is not None:
        db_user.surname = user_update.surname
    if user_update.username is not None:
        db_user.username = user_update.username
    if user_update.birth_date is not None:
        db_user.birth_date = user_update.birth_date
    
    # Email change logic
    if user_update.email is not None and user_update.email != db_user.email:
        # Check if email taken
        existing_user = db.query(models.User).filter(models.User.email == user_update.email).first()
        if existing_user:
             raise HTTPException(status_code=400, detail="Email already pending or taken")
        
        db_user.pending_email = user_update.email
        db_user.verification_token = str(uuid.uuid4())
        # We generally don't set is_verified = False here because the OLD email is still valid until verified.
        # But we send a verification email to the NEW address.
        EmailService.send_verification_email(db_user.pending_email, db_user.verification_token)
        # Note: Frontend should notify user "Verification sent to new email"

    # Obsługa zdjęcia profilowego
    if user_update.profile_image_path is not None:
        db_user.profile_image_path = user_update.profile_image_path

    # Obsługa trybu ciemnego
    if user_update.is_dark_mode is not None:
        print(f"Updating dark mode to: {user_update.is_dark_mode}")
        db_user.is_dark_mode = user_update.is_dark_mode

    # Obsługa zmiany hasła
    if user_update.password:
        if not user_update.old_password:
             raise HTTPException(status_code=400, detail="Old password is required to set new password")
        if not pwd_context.verify(user_update.old_password, db_user.hashed_password):
             raise HTTPException(status_code=400, detail="Invalid old password")
        
        db_user.hashed_password = pwd_context.hash(user_update.password)

    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=204)
def delete_user_account(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Usuwamy użytkownika (kaskada usunie powiązane wpisy, jeśli tak skonfigurowano bazę,
    # w przeciwnym razie trzeba ręcznie usunąć wpisy z moods/sobriety)
    db.delete(db_user)
    db.commit()
    return