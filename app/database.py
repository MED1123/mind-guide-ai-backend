from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(override=True)

# Prioritize env var, fallback to local sqlite
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./mood_journal.db")

# Force pg8000 (pure python) driver if using postgresql
if "postgresql" in SQLALCHEMY_DATABASE_URL:
    if "5432" in SQLALCHEMY_DATABASE_URL:
        print("WARNING: Detected failing Direct Connection (Port 5432). Automatically switching to Transaction Pooler (Port 6543).")
        SQLALCHEMY_DATABASE_URL = "postgresql://postgres.xeffplmojuztfcydxcso:silnehaslo123@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
    
    print(f"DEBUG: Connecting to {SQLALCHEMY_DATABASE_URL.split('@')[-1]}")
    if "postgresql://" in SQLALCHEMY_DATABASE_URL:
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+pg8000://")
    
    # Remove 'pgbouncer' parameter which is unsupported by pg8000
    try:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(SQLALCHEMY_DATABASE_URL)
        qs = parse_qs(parsed.query)
        if 'pgbouncer' in qs:
            del qs['pgbouncer']
            new_query = urlencode(qs, doseq=True)
            SQLALCHEMY_DATABASE_URL = urlunparse(parsed._replace(query=new_query))
    except ImportError:
        # Fallback if libraries are missing (unlikely)
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")

connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Initialize Supabase Client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY missing in .env. Auth will fail.")
    supabase = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"ERROR: Failed to initialize Supabase client: {e}")
        supabase = None