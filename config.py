import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
APP_URL = os.getenv("APP_URL", "http://localhost:8501")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

MEM0_API_KEY = os.getenv("MEM0_API_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing.")

if not SUPABASE_ANON_KEY:
    raise RuntimeError("SUPABASE_ANON_KEY is missing.")

if not SUPABASE_DB_URL:
    raise RuntimeError("SUPABASE_DB_URL is missing.")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing.")

if not MEM0_API_KEY:
    raise RuntimeError("MEM0_API_KEY is missing from the environment.")



      