from app.database import engine, Base
from app import models # Import models to register them with Base

def create_tables():
    print("--- CREATING TABLES ---")
    try:
        Base.metadata.create_all(bind=engine)
        print("SUCCESS: Tables created.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    create_tables()
