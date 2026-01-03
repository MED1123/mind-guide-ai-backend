from app.database import engine
from sqlalchemy import text

def fix_schema():
    print("--- Fixing Database Schema & Cleaning Legacy Data ---")
    commands = [
        # 1. Truncate tables to remove integer-ID data that conflicts with UUIDs
        "TRUNCATE TABLE public.mood_entries, public.sobriety_clocks, public.ai_analysis_cache RESTART IDENTITY CASCADE;",
        "TRUNCATE TABLE public.users RESTART IDENTITY CASCADE;",
        
        # 2. Fix MoodEntry Column (Drop int owner_id, Rename uuid user_id -> owner_id)
        "ALTER TABLE public.mood_entries DROP COLUMN IF EXISTS owner_id;",
        "ALTER TABLE public.mood_entries RENAME COLUMN user_id TO owner_id;",
        
        # 3. Ensure User ID is UUID (if not already) - this requires empty table usually
        "ALTER TABLE public.users ALTER COLUMN id TYPE uuid USING id::text::uuid;"
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            try:
                print(f"Executing: {cmd}")
                conn.execute(text(cmd))
                conn.commit()
                print("OK")
            except Exception as e:
                print(f"ERROR: {e}")
                # Don't abort, some might fail if already done

if __name__ == "__main__":
    fix_schema()
