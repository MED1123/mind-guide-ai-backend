from fastapi import FastAPI
from app import models, database
from app.routers import auth, entries, ai

models.Base.metadata.create_all(bind=database.engine)

# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="Mood Journal API",
    description="Backend w Pythonie (FastAPI) dla aplikacji Mood Journal.",
    version="1.0.0"
)

# --- PODŁĄCZANIE ROUTERÓW ---
# Dzięki temu aplikacja "widzi" endpointy zdefiniowane w innych plikach
app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(ai.router)

# --- ENDPOINTY PODSTAWOWE ---

@app.get("/")
def read_root():
    """
    Sprawdza, czy serwer działa.
    """
    return {
        "message": "Mood Journal API działa poprawnie! 🚀",
        "info": "Dokumentacja dostępna pod adresem /docs"
    }

@app.get("/health")
def health_check():
    """
    Endpoint dla monitoringu (np. Google Cloud/AWS sprawdza to co chwila).
    """
    return {"status": "ok"}