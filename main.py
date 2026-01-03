from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from app import models, database
from app.routers import auth, entries, ai, users, sobriety

# import add_email_columns # Auto-run migration
# add_email_columns.migrate()

# import add_reset_token
# add_reset_token.migrate()

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(entries.router)
app.include_router(ai.router)
# Rejestracja nowego routera
app.include_router(users.router)
app.include_router(sobriety.router)

@app.get("/")
def read_root():
    return {"message": "Mood Journal API is running!", "routes": [route.path for route in app.routes]}