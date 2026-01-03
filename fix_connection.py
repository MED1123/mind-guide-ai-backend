import os

env_path = ".env"
target_url = "postgresql://postgres.xeffplmojuztfcydxcso:silnehaslo123@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"

print("--- CURRENT .env CONTENT ---")
try:
    with open(env_path, "r") as f:
        print(f.read())
except FileNotFoundError:
    print(".env file not found!")

print("\n--- OVERWRITING .env ---")
with open(env_path, "w") as f:
    f.write(f'SQLALCHEMY_DATABASE_URL="{target_url}"\n')
    f.write('RESEND_API_KEY="re_a4k1..."\n')
    f.write('SUPABASE_URL="https://xeffplmojuztfcydxcso.supabase.co"\n')
    f.write('SUPABASE_KEY="sb_publishable_E5gbt9TSwy9tCCA6rudUYw_Nu7cqizg"\n')

print("--- NEW .env CONTENT ---")
with open(env_path, "r") as f:
    print(f.read())
