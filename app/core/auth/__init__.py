'''Functions for Authentication for the Apps'''
from functools import wraps

def auth_check_decorator(func):
    '''checks a predefined token in request header'''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # To be implemented.
        # Uses Supabase, gets user roles
        # Verify the DB requesting to connect to and sources listed for querying are permissible
        # Raises 403 error for unauthorized access
        # Passes the list of accessible sources to the calling function
        return await func(*args, **kwargs)
    return wrapper
