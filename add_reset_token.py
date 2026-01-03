from app import database, models
from sqlalchemy import text

def migrate():
    print("Migrating: Adding reset_token column...")
    with database.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR"))
            conn.commit()
            print("Successfully added reset_token column.")
        except Exception as e:
            print(f"Column might already exist or error: {e}")

if __name__ == "__main__":
    migrate()
