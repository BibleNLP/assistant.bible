'''Functions for Authentication for the Apps'''
import os
from functools import wraps
from custom_exceptions import PermissionException
import gotrue.errors

from supabase import create_client, Client


def admin_auth_check_decorator(func):
    '''For all data managment APIs'''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract the access token from the request headers
        access_token = kwargs.get('token')
        if not access_token:
            raise ValueError("Access token is missing")
        access_token_str = access_token.get_secret_value()
        # Verify the access token using Supabase secret
        supabase_url: str = os.environ.get("SUPABASE_URL")
        supabase_key: str = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(supabase_url, supabase_key)
        try:
            user_data = supabase.auth.get_user(access_token_str)
        except gotrue.errors.AuthApiError as e:
            raise PermissionException("Unauthorized access. Invalid token.") from e

        if user_data.user_metadata.get('user_type') != 'admin':
            raise PermissionException("Unauthorized access. User is not admin.")

        return await func(*args, **kwargs)

    return wrapper


def chatbot_auth_check_decorator(func):
    '''checks a predefined token in request header, and checks it is a
    valid, logged in, user.
    '''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract the access token from the request headers
        access_token = kwargs.get('token')
        if not access_token:
            raise ValueError("Access token is missing")
        access_token_str = access_token.get_secret_value()

        # Verify the access token using Supabase secret
        supabase_url: str = os.environ.get("SUPABASE_URL")
        supabase_key: str = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(supabase_url, supabase_key)
        try:
            supabase.auth.get_user(access_token_str)
        except gotrue.errors.AuthApiError as e:
            raise PermissionException("Unauthorized access. Invalid token.") from e

        return await func(*args, **kwargs)

    return wrapper


def chatbot_get_labels_decorator(func):
    '''checks a predefined token in request header, and returns available sources.
    '''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract the access token from the request headers
        access_token = kwargs.get('token')
        if not access_token:
            raise ValueError("Access token is missing")
        access_token_str = access_token.get_secret_value()

        # Verify the access token using Supabase secret
        supabase_url: str = os.environ.get("SUPABASE_URL")
        supabase_key: str = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(supabase_url, supabase_key)
        try:
            user_data = supabase.auth.get_user(access_token_str)

        except gotrue.errors.AuthApiError as e: # The user is not logged in
            labels = ['public']

        else:
            result = supabase.table('userTypes').select('''
                    sources
                    '''
                ).eq(
                'user_type', user_data.user.user_metadata.get('user_type')
                ).limit(1).single().execute()
            labels = result.data.get('sources')

        kwargs['label'] = labels
        # Proceed with the original function call and pass the sources to it
        return await func(*args, **kwargs)

    return wrapper
