from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime # <--- WAŻNY NOWY IMPORT
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

# Dodawanie wpisu

class DeleteByContentRequest(schemas.BaseModel):
    user_id: str
    text: str
    date: datetime

@router.post("/delete_by_content", status_code=200)
def delete_entry_by_content(
    request: DeleteByContentRequest,
    db: Session = Depends(get_db)
):
    # Szukamy wpisu dla danego usera
    # Tolerancja czasowa: 60 sekund
    # Tekst musi pasować dokładnie (lub można dodać fuzzy matching w przyszłości)
    
    entries = db.query(models.MoodEntry).filter(
        models.MoodEntry.owner_id == request.user_id,
        models.MoodEntry.text == request.text
    ).all()
    
    deleted_count = 0
    
    for entry in entries:
        # Oblicz różnicę czasu
        # entry.date w bazie może być naive lub offset-aware. Przyjmujemy założenie, że są w tej samej strefie (lub UTC).
        # Konwersja na timestamp dla bezpiecznego porównania
        
        # Jeśli entry.date nie ma strefy, a input ma, lub odwrotnie -> crash.
        # Użyjmy bezpieczniejszego podejścia:
        
        db_date = entry.date
        input_date = request.date
        
        # Make timestamps naive for simple diff
        if db_date.tzinfo:
            db_date = db_date.replace(tzinfo=None)
        if input_date.tzinfo:
            input_date = input_date.replace(tzinfo=None)
            
        diff = abs((db_date - input_date).total_seconds())
        
        if diff < 120: # 2 minuty tolerancji
            db.delete(entry)
            deleted_count += 1
            
    if deleted_count > 0:
        db.commit()
        return {"message": f"Deleted {deleted_count} entries"}
    else:
        # Instead of 404, we return success 200 with 0 count to avoid frontend errors if it's already gone.
        # But for logic flow, let's keep it as is or return false? 
        # Frontend expects 200 for "success".
        # If not found, it means it's already gone (success) or mismatch.
        # Let's return 200 but say 0 deleted? Or 404? 
        # The current frontend prints "Nie znaleziono" on non-200.
        # Let's keep 404 for now to indicate "nothing matched".
        raise HTTPException(status_code=404, detail="No matching entry found")

@router.post("/{user_id}", response_model=schemas.MoodEntry)
def create_entry_for_user(
    user_id: str, 
    entry: schemas.MoodEntryCreate, 
    db: Session = Depends(get_db)
):
    # 1. Logika Daty:
    # Jeśli frontend przysłał datę (np. z generatora testowego), używamy jej.
    # Jeśli nie (entry.date jest None), używamy aktualnego czasu.
    final_date = entry.date if entry.date else datetime.now()

    # 2. Obsługa zdjęć:
    # Konwersja listy zdjęć na string (np. "img1.jpg|img2.jpg") do zapisu w bazie
    images_str = "|".join(entry.image_paths) if entry.image_paths else ""

    # 3. Tworzenie obiektu bazy danych
    db_entry = models.MoodEntry(
        date=final_date,          # <--- TUTAJ PRZEKAZUJEMY DATĘ
        text=entry.text,
        mood_rating=entry.mood_rating,
        category=entry.category,
        image_paths=images_str, 
        owner_id=user_id,
        # Pola domyślne wymagane przez model (jeśli nie ma ich w schemas.create)
        ai_analysis="",
        conversation=""
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    # 4. Przygotowanie odpowiedzi:
    # Musimy ręcznie skonstruować obiekt odpowiedzi, aby upewnić się, 
    # że 'image_paths' wraca jako lista, a nie string z bazy.
    return schemas.MoodEntry(
        id=db_entry.id,
        date=db_entry.date,
        text=db_entry.text,
        mood_rating=db_entry.mood_rating,
        category=db_entry.category,
        ai_analysis=db_entry.ai_analysis,
        conversation=db_entry.conversation,
        # Konwersja stringa "a|b" na listę ["a", "b"]
        image_paths=db_entry.image_paths.split("|") if db_entry.image_paths else [],
        owner_id=db_entry.owner_id
    )

@router.get("/{user_id}", response_model=List[schemas.MoodEntry])
def read_entries(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Filtrujemy po owner_id == user_id
    entries = db.query(models.MoodEntry)\
        .filter(models.MoodEntry.owner_id == user_id)\
        .order_by(models.MoodEntry.date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Konwersja stringa z bazy z powrotem na listę dla każdego wpisu
    # (Pydantic oczekuje listy, baza zwraca string)
    results = []
    for entry in entries:
        try:
            # Tworzymy obiekt schematu ręcznie lub modyfikujemy obiekt SQLAlchemy
            # Najbezpieczniej jest zmapować to na schema:
            img_list = entry.image_paths.split("|") if entry.image_paths else []
            
            # Weryfikacja krytycznych pól (aby uniknąć błędu walidacji Pydantic)
            # Jeśli np. mood_rating jest w bazie NULL, a schema wymaga float, to tu wybuchnie.
            # Dzięki try-except pominiemy uszkodzone wpisy.
            
            results.append(schemas.MoodEntry(
                id=entry.id,
                date=entry.date,
                text=entry.text if entry.text is not None else "", # Fallback for text
                mood_rating=entry.mood_rating if entry.mood_rating is not None else 0.0, # Fallback
                category=entry.category if entry.category is not None else "Nieznane", # Fallback
                ai_analysis=entry.ai_analysis,
                conversation=entry.conversation,
                image_paths=img_list,
                owner_id=entry.owner_id
            ))
        except Exception as e:
            print(f"Skipping corrupt entry ID {entry.id}: {e}")
            continue
    
    return results

@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.MoodEntry).filter(models.MoodEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    db.delete(db_entry)
    db.commit()
    return



@router.put("/{entry_id}", response_model=schemas.MoodEntry)
def update_entry(entry_id: int, entry_update: schemas.MoodEntryCreate, db: Session = Depends(get_db)):
    # Note: MoodEntryCreate is used as the schema here for simplicity, 
    # but theoretically we should use a MoodEntryUpdate schema if fields were different.
    # Since we update text/images typically, it's fine.
    
    db_entry = db.query(models.MoodEntry).filter(models.MoodEntry.id == entry_id).first()
    if not db_entry:
         raise HTTPException(status_code=404, detail="Entry not found")
    
    # Update fields
    # We update text, images, conversation, ai_analysis if needed.
    # We generally don't update date, mood_rating, category for existing entries (unless requested),
    # but let's allow updating everything passed in proper format.
    
    if entry_update.text is not None:
        db_entry.text = entry_update.text
        
    # Images come as list in schema, joined string in DB
    if entry_update.image_paths is not None:
        db_entry.image_paths = "|".join(entry_update.image_paths)
        
    # For now, we assume other fields like mood_rating might stay same or update if user changed logic.
    # In EditScreen we usually only edit text/images.
    # But let's check what EditScreen allows.
    
    if entry_update.image_paths is not None:
        db_entry.image_paths = "|".join(entry_update.image_paths)
        
    if entry_update.conversation is not None:
        db_entry.conversation = entry_update.conversation
        
    if entry_update.ai_analysis is not None:
        db_entry.ai_analysis = entry_update.ai_analysis
    
    db.commit()
    db.refresh(db_entry)
    
    # Return formatted matched to response_model
    img_list = db_entry.image_paths.split("|") if db_entry.image_paths else []
    return schemas.MoodEntry(
        id=db_entry.id,
        date=db_entry.date,  
        text=db_entry.text,
        mood_rating=db_entry.mood_rating,
        category=db_entry.category,
        ai_analysis=db_entry.ai_analysis,
        conversation=db_entry.conversation,
        image_paths=img_list,
        owner_id=db_entry.owner_id
    )