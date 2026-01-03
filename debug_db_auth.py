import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pg8000

# Load existing .env
load_dotenv()

url = os.getenv("SQLALCHEMY_DATABASE_URL")
if not url:
    print("ERROR: SQLALCHEMY_DATABASE_URL not found in .env")
    exit(1)

print(f"Current URL from .env (masked): {url.split(':')[0]}:***@...")

def test_connection(connection_url):
    try:
        # Force pg8000
        if connection_url.startswith("postgresql://"):
            connection_url = connection_url.replace("postgresql://", "postgresql+pg8000://")
        
        print(f"Attempting connection... ")
        engine = create_engine(connection_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            print("SUCCESS! Connection established.")
            print(f"Server version: {result.fetchone()[0]}")
            return True
    except Exception as e:
        print(f"CONNECTION FAILED: {e}")
        return False

# 1. Test existing URL
print("\n--- Testing .env configuration ---")
if test_connection(url):
    print("The .env file seems correct. The issue might be elsewhere.")
else:
    print("\n--- Interactive Debugging ---")
    print("The current .env settings failed.")
    print("It is likely that your password contains special characters that need escaping.")
    
    # Prase existing URL to preserve host/user/db
    try:
        # Expected format: postgresql://user:pass@host:port/db
        # We'll just ask for the components to be safe
        user_input = input("Enter your Database User (default: postgres): ") or "postgres"
        try:
             # Try to parse host/port from existing url if possible
             pass
        except:
             pass
             
        host_input = input("Enter Database Host (e.g., aws-0-eu-central-1.pooler.supabase.com): ")
        port_input = input("Enter Database Port (default: 6543): ") or "6543"
        db_input = input("Enter Database Name (default: postgres): ") or "postgres"
        password_input = input("Enter your Database PASSWORD (will be URL encoded): ")
        
        # URL Encode password
        encoded_password = urllib.parse.quote_plus(password_input)
        
        # Construct new URL
        new_url = f"postgresql://{user_input}:{encoded_password}@{host_input}:{port_input}/{db_input}"
        
        print(f"\nTesting generated URL: postgresql://{user_input}:[MASKED]@{host_input}:{port_input}/{db_input}")
        
        if test_connection(new_url):
            print("\n!!! SUCCESS !!!")
            print("Your correct connection string is:")
            print("-" * 60)
            print(new_url)
            print("-" * 60)
            print("Copy the line above and replace SQLALCHEMY_DATABASE_URL in your .env file.")
            
            # Automatically update .env?
            # maybe risky, better let user do it.
    except KeyboardInterrupt:
        print("\nAborted.")
