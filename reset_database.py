from app.database import engine
from sqlalchemy import text

def reset_database():
    print("--- DROPPING ALL TABLES TO FORCE SCHEMA RECREATION ---")
    commands = [
        "DROP TABLE IF EXISTS public.sobriety_clocks CASCADE;",
        "DROP TABLE IF EXISTS public.ai_analysis_cache CASCADE;",
        "DROP TABLE IF EXISTS public.mood_entries CASCADE;",
        "DROP TABLE IF EXISTS public.users CASCADE;"
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

if __name__ == "__main__":
    reset_database()
