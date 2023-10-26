"""Supabase connection module."""

import os
from supabase import create_client, Client
import gotrue.errors

def connect_to_supabase() -> Client:
    """
    Connects to Supabase using the URL and key stored in environment variables.

    Returns:
    supa (Client): A Supabase client object.
    """
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supa: Client = create_client(url, key)
    return supa
