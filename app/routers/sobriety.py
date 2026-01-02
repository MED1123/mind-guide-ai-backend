from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from .. import models, database

router = APIRouter(
    prefix="/sobriety",
    tags=["sobriety"]
)

class SobrietyClockCreate(BaseModel):
    user_id: int
    addiction_type: str
    custom_name: Optional[str] = ""
    start_date: datetime

class SobrietyClockReset(BaseModel):
    new_date: datetime

class SobrietyClockResponse(BaseModel):
    id: int
    user_id: int
    addiction_type: str
    custom_name: str
    start_date: datetime
    created_at: datetime

    class Config:
        orm_mode = True

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/clocks", response_model=SobrietyClockResponse)
def create_clock(clock: SobrietyClockCreate, db: Session = Depends(get_db)):
    db_clock = models.SobrietyClock(
        user_id=clock.user_id,
        addiction_type=clock.addiction_type,
        custom_name=clock.custom_name,
        start_date=clock.start_date
    )
    db.add(db_clock)
    db.commit()
    db.refresh(db_clock)
    return db_clock

@router.get("/clocks/{user_id}", response_model=List[SobrietyClockResponse])
def get_user_clocks(user_id: int, db: Session = Depends(get_db)):
    clocks = db.query(models.SobrietyClock)\
        .filter(models.SobrietyClock.user_id == user_id)\
        .order_by(desc(models.SobrietyClock.created_at))\
        .all()
    return clocks

@router.delete("/clocks/{clock_id}")
def delete_clock(clock_id: int, db: Session = Depends(get_db)):
    clock = db.query(models.SobrietyClock).filter(models.SobrietyClock.id == clock_id).first()
    if not clock:
        raise HTTPException(status_code=404, detail="Clock not found")
    
    db.delete(clock)
    db.commit()
    return {"message": "Clock deleted"}

@router.put("/clocks/{clock_id}/reset")
def reset_clock(clock_id: int, reset_data: SobrietyClockReset, db: Session = Depends(get_db)):
    clock = db.query(models.SobrietyClock).filter(models.SobrietyClock.id == clock_id).first()
    if not clock:
        raise HTTPException(status_code=404, detail="Clock not found")
    
    clock.start_date = reset_data.new_date
    db.commit()
    db.refresh(clock)
    return {"message": "Clock reset successfully", "new_start_date": clock.start_date}
