import sqlite3
import os

DB_FILE = "./mood_journal.db"

def add_column_if_not_exists(cursor, table, column, definition):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"Added column {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding {column}: {e}")

def migrate():
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found!")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Running migration for Email Verification...")

    # is_verified (Boolean, default False) -> Integer 0/1 in SQLite
    add_column_if_not_exists(cursor, "users", "is_verified", "BOOLEAN DEFAULT 0")

    # verification_token (String, nullable)
    add_column_if_not_exists(cursor, "users", "verification_token", "VARCHAR")

    # pending_email (String, nullable) - for email change requests
    add_column_if_not_exists(cursor, "users", "pending_email", "VARCHAR")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
