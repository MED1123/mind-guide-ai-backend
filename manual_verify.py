import sqlite3
import os

DB_FILE = "./mood_journal.db"
TARGET_EMAIL = "norbixd100@interia.pl"

if os.path.exists(DB_FILE):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (TARGET_EMAIL,))
        
        if cursor.rowcount > 0:
            print(f"Successfully verified user: {TARGET_EMAIL}", flush=True)
        else:
            print(f"User not found: {TARGET_EMAIL}", flush=True)
            # List all emails to see what's there
            cursor.execute("SELECT email FROM users")
            print("Existing users:", [r[0] for r in cursor.fetchall()], flush=True)
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating DB: {e}", flush=True)
else:
    print("Database file not found.")
