'''Functions for Authentication for the Apps'''
import os
from functools import wraps
from custom_exceptions import PermissionException

from supabase import create_client, Client


def admin_auth_check_decorator(func):
    '''For all data managment APIs'''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        token = kwargs.get('token')
        if token.get_secret_value() != os.getenv('ADMIN_ACCESS_TOKEN', "chatchatchat"):
            raise PermissionException("Wrong access token!!!")
        return await func(*args, **kwargs)
    return wrapper


def chatbot_auth_check_decorator(func):
    '''checks a predefined token in request header'''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # To be implemented.
        # Uses Supabase, gets user roles
        # Verify the DB requesting to connect to and sources listed for querying are permissible
        # Raises 403 error for unauthorized access
        # Passes the list of accessible sources to the calling function

        # url: str = os.environ.get("SUPABASE_URL")
        # key: str = os.environ.get("SUPABASE_KEY")
        # supabase: Client = create_client(url, key)

        # email: str = kwargs.get('email')
        # password: str = kwargs.get('password')
        # email = 'woodwardmw@gmail.com'
        # password = 'password'
        # try:
        #     data = supabase.auth.sign_in_with_password({ "email": email, "password": password})
        # except Exception as e:
        #     raise PermissionException("Cannot authenticate user in Supabase")
        # session = supabase.auth.get_session(data['access_token'])

        # Until Supabase or something else is ready
        token = kwargs.get('token')
        if token.get_secret_value() != os.getenv('CHATBOT_ACCESS_TOKEN', "chatchatchat"):
            raise PermissionException("Wrong access token!!!")
        return await func(*args, **kwargs)
    return wrapper
