import sqlite3
import os

db_path = 'mood_journal.db'
log_file = 'migration_log.txt'

with open(log_file, 'w') as f:
    if not os.path.exists(db_path):
        f.write(f"DB not found at {os.getcwd()}/{db_path}\n")
    else:
        f.write(f"DB found at {os.getcwd()}/{db_path}\n")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_dark_mode BOOLEAN DEFAULT 0")
                conn.commit()
                f.write("Migration successful.\n")
            except Exception as e:
                f.write(f"Migration failed (maybe already done?): {e}\n")
            
            # Check columns
            cursor.execute("PRAGMA table_info(users)")
            cols = [row[1] for row in cursor.fetchall()]
            f.write(f"Columns: {cols}\n")
            conn.close()
        except Exception as e:
            f.write(f"Connection failed: {e}\n")
