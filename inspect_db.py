import sqlite3
import os

DB_FILE = "./mood_journal.db"

if not os.path.exists(DB_FILE):
    print(f"FILE NOT FOUND: {DB_FILE}")
else:
    print(f"FILE EXISTS: {DB_FILE}")
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        print("\nTables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            print(f"- {t[0]}")
            
        print("\nColumns in 'users':")
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        for c in columns:
            print(c)

        print("\nRows in 'users':")
        cursor.execute("SELECT id, email, is_verified FROM users;")
        rows = cursor.fetchall()
        print(f"Total users: {len(rows)}")
        for r in rows:
            print(r)
            
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")
