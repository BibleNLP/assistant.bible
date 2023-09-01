'''Functions for Authentication for the Apps'''
import os
from functools import wraps
from custom_exceptions import PermissionException
import gotrue.errors
from fastapi import WebSocket

from core.auth.supabase import supa
from log_configs import log
import schema


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
        try:
            user_data = supa.auth.get_user(access_token_str)

        except gotrue.errors.AuthApiError as e:
            raise PermissionException("Unauthorized access. Invalid token.") from e
        else:
            result = supa.table('adminUsers').select('''
                    user_id
                    '''
                ).eq(
                'user_id', user_data.user.id
                ).execute()
        if not result.data:
            raise PermissionException("Unauthorized access. User is not admin.")

        return await func(*args, **kwargs)

    return wrapper


def chatbot_auth_check_decorator(func):
    '''checks a predefined token in request header, and checks it is a
    valid, logged in, user.
    '''
    @wraps(func)
    async def wrapper(websocket: WebSocket, *args, **kwargs):
        # Extract the access token from the request headers
        access_token = kwargs.get('token')
        if not access_token:
            raise ValueError("Access token is missing")
        access_token_str = access_token.get_secret_value()

        # Verify the access token using Supabase secret
        try:
            supa.auth.get_user(access_token_str)
        except gotrue.errors.AuthApiError as e:
            await websocket.accept()
            json_response = schema.BotResponse(sender=schema.SenderType.BOT,
                    message='Please sign in first. I look forward to answering your questions.', type=schema.ChatResponseType.ANSWER,
                    sources=[],
                    media=[])
            await websocket.send_json(json_response.dict())
            return
        return await func(websocket, *args, **kwargs)

    return wrapper


def chatbot_get_labels_decorator(func):
    '''checks a predefined token in request header, and returns available sources.
    '''
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract the access token from the request headers
        access_token = kwargs.get('token')
        if not access_token:
            labels = []
        else:
            access_token_str = access_token.get_secret_value()

            # Verify the access token using Supabase secret
            try:
                user_data = supa.auth.get_user(access_token_str)

            except gotrue.errors.AuthApiError as e: # The user is not logged in
                labels = []

            else:
                result = supa.table('userAttributes').select('id, user_id, user_type, "userTypes"(user_type, sources)').eq('user_id', user_data.user.id).execute()
                labels = []
                for data in result.data:
                    labels.extend(data.get('userTypes', {}).get('sources', []))
                print(f'{labels=}')
        labels = list(set(labels))
        kwargs['labels'] = labels
        # Proceed with the original function call and pass the sources to it
        return await func(*args, **kwargs)

    return wrapper
