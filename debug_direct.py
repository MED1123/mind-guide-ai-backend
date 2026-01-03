import os
import urllib.parse
from sqlalchemy import create_engine, text
import pg8000

print("\n--- Testing Direct Connection (Port 5432) ---")
print("This bypasses the Transaction Pooler (Supavisor) and connects directly to the DB.")
print("This is often more reliable for local development.")

# Credentials from previous context
# You can change these if they are wrong
project_ref = input("Enter Project Reference ID (e.g., rwgautpkkzpeytfvehdz): ") or "rwgautpkkzpeytfvehdz"
password_input = input("Enter Database Password: ") or "V?u5WBUqn!pNf9A?sjzD"

# Construct Direct URL
# Host: db.[ref].supabase.co
# Port: 5432
# User: postgres (no suffix needed for direct)
user = "postgres"
host = f"db.{project_ref}.supabase.co"
port = "5432"
db = "postgres"

encoded_password = urllib.parse.quote_plus(password_input)
connection_url = f"postgresql+pg8000://{user}:{encoded_password}@{host}:{port}/{db}"

print(f"\nTesting URL: postgresql+pg8000://{user}:[MASKED]@{host}:{port}/{db}")

try:
    engine = create_engine(connection_url, connect_args={'ssl_context': True}) # SSL is required for Supabase
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print("\n!!! SUCCESS !!!")
        print("Connection established via Direct Connection.")
        print(f"Server version: {result.fetchone()[0]}")
        print("-" * 60)
        print("Use this URL in your .env:")
        print(connection_url.replace("+pg8000", "")) # Remove driver for .env compatibility if code adds it 
        print("-" * 60)
except Exception as e:
    print(f"\nCONNECTION FAILED: {e}")
    print("\nPossible causes:")
    print("1. Wrong Password")
    print("2. Wrong Project Reference")
    print("3. Firewall waiting to allow IP (unlikely for Supabase default)")
