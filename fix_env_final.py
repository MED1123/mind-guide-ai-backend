import os

env_path = ".env"

# Correct values
content = """OPENROUTER_API_KEY=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
SQLALCHEMY_DATABASE_URL="postgresql://postgres.xeffplmojuztfcydxcso:silnehaslo123@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
SUPABASE_URL="https://xeffplmojuztfcydxcso.supabase.co"
SUPABASE_KEY="sb_publishable_E5gbt9TSwy9tCCA6rudUYw_Nu7cqizg"
SMTP_USER="noreplymoodjournal@gmail.com"
SMTP_PASSWORD="emhm eixn jazl nmes"
"""

print("--- RESTORING .env ---")
with open(env_path, "w") as f:
    f.write(content)

print("--- NEW .env CONTENT ---")
with open(env_path, "r") as f:
    print(f.read())
