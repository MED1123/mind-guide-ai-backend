import sqlite3
import os

DB_FILE = "./mood_journal.db"

if os.path.exists(DB_FILE):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Order matters if there are foreign key constraints involved (delete children first)
        tables = ["mood_entries", "ai_analysis_cache", "sobriety_clocks", "users"]
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f"Deleted all records from {table}", flush=True)
            except Exception as e:
                print(f"Error deleting from {table}: {e}", flush=True)
                
        conn.commit()
        conn.close()
        print("Database reset complete.", flush=True)
    except Exception as e:
        print(f"Error connecting to DB: {e}", flush=True)
else:
    print("Database file not found.")
