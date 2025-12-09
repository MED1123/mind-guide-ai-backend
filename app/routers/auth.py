from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from passlib.context import CryptContext
from pydantic import BaseModel

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- REJESTRACJA ---
@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    
    new_user = models.User(
        email=user.email, 
        username=user.username, # <--- ZAPISUJEMY USERNAME
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- LOGOWANIE ---
class LoginResponse(BaseModel):
    user_id: int
    email: str
    message: str

@router.post("/login", response_model=LoginResponse)
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Uwaga: Schemat UserCreate wymaga teraz username, ale przy logowaniu
    # Flutter może wysłać pusty ciąg lub cokolwiek w polu username,
    # ponieważ tutaj sprawdzamy tylko email i hasło.
    
    # 1. Szukamy użytkownika
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Nieprawidłowy email lub hasło")
    
    # 2. Weryfikujemy hasło
    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Nieprawidłowy email lub hasło")
    
    # 3. Sukces! Zwracamy ID
    return {
        "user_id": db_user.id,
        "email": db_user.email,
        "message": "Zalogowano pomyślnie"
    }