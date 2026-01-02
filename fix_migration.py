import sqlite3

conn = sqlite3.connect('mood_journal.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_dark_mode BOOLEAN DEFAULT 0")
    conn.commit()
    print("Migration successful: Added is_dark_mode column.")
except Exception as e:
    print(f"Migration failed (maybe column exists?): {e}")

conn.close()
