from app.database import engine
from sqlalchemy import inspect, text

def check_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("--- Database Verification ---")
    print(f"Connected to: {engine.url.render_as_string(hide_password=True).split('@')[-1]}")
    print(f"Tables found: {tables}")
    
    if "users" in tables:
        print("SUCCESS: 'users' table exists.")
        
        # Check user count
        with engine.connect() as conn:
            result = conn.execute(text("SELECT count(*) FROM users"))
            count = result.scalar()
            print(f"Current user count: {count}")
    else:
        print("ERROR: 'users' table NOT found. Migration might have failed.")

if __name__ == "__main__":
    check_tables()
