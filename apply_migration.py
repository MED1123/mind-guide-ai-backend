from app.database import engine
from sqlalchemy import text

def apply_migration():
    sql_commands = [
        # 1. Poprawa tabeli mood_entries
        """
        ALTER TABLE public.mood_entries 
        ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users(id) DEFAULT auth.uid();
        """,
        
        # 2. Poprawa tabeli sobriety_clocks
        """
        ALTER TABLE public.sobriety_clocks 
        ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users(id) DEFAULT auth.uid();
        """,
        
        # 3. Poprawa tabeli ai_analysis_cache
        """
        ALTER TABLE public.ai_analysis_cache 
        ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users(id) DEFAULT auth.uid();
        """,
        
        # 4.a Remove unused columns from users (public)
        """ALTER TABLE public.users DROP COLUMN IF EXISTS hashed_password;""",
        """ALTER TABLE public.users DROP COLUMN IF EXISTS verification_token;""",
        """ALTER TABLE public.users DROP COLUMN IF EXISTS reset_token;""",
        """ALTER TABLE public.users DROP COLUMN IF EXISTS pending_email;""",
        
        # 4.b Migrate users.id to UUID
        # Note: This might fail if there is existing data with integer IDs that cannot be cast.
        # But since we just started fresh or have little data, we try. 
        # If it fails, we might need to truncate or handle differently.
        # For a clean start, we can TRUNCATE (User OK'd fresh config).
        # Let's try direct casting first.
        """
        ALTER TABLE public.users 
        ALTER COLUMN id TYPE uuid USING id::text::uuid;
        """,
        
        # 5. Aktywacja RLS
        """ALTER TABLE public.mood_entries ENABLE ROW LEVEL SECURITY;""",
        """ALTER TABLE public.sobriety_clocks ENABLE ROW LEVEL SECURITY;""",
        
        # 6. Policies (Drop first to avoid errors if exist)
        """DROP POLICY IF EXISTS "Manage own mood entries" ON public.mood_entries;""",
        """
        CREATE POLICY "Manage own mood entries" ON public.mood_entries
        FOR ALL TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
        """,
        
        """DROP POLICY IF EXISTS "Manage own clocks" ON public.sobriety_clocks;""",
        """
        CREATE POLICY "Manage own clocks" ON public.sobriety_clocks
        FOR ALL TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
        """
    ]

    print("--- Applying SQL Migration ---")
    with engine.connect() as conn:
        for cmd in sql_commands:
            try:
                print(f"Executing: {cmd.strip().splitlines()[0]}...")
                conn.execute(text(cmd))
                conn.commit()
                print("OK")
            except Exception as e:
                print(f"ERROR: {e}")
                # Don't stop, try others (idempotency is handled by IF NOT EXISTS usually, but some might fail)

if __name__ == "__main__":
    apply_migration()
