import sqlite3
try:
    conn = sqlite3.connect('mood_journal.db')
    cursor = conn.cursor()
    cursor.execute("SELECT is_dark_mode FROM users LIMIT 1")
    print("Column exists!")
except Exception as e:
    print(f"Error: {e}")
