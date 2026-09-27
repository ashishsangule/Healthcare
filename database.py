import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("https://kubyedexweoutzsteaas.supabase.co/rest/v1/")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1YnllZGV4d2VvdXR6c3RlYWFzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5MDUyMzcxNCwiZXhwIjoyMTA2MDk5NzE0fQ.9nuEdNrDCBiOnG2di2FkM4CnTdKIoh8kAKvLPTKB6H8")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY are required")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def get_db():
    return supabase


def init_db():
    # Tables are created directly in Supabase SQL Editor.
    pass