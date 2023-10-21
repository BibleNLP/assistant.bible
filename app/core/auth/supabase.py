import os
from supabase import create_client, Client
import gotrue.errors

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supa: Client = create_client(url, key)
