"""Functions for Authentication for the Apps"""
import os
from functools import wraps
from custom_exceptions import PermissionException, SupabaseException
from fastapi import WebSocket

from log_configs import log
import schema

# pylint: disable=too-few-public-methods, unused-argument


class AuthInterface:
    """Common methods and signatures for user authentication and access management"""

    def __init__(self):
        """Connects to 3rd party auth service or respective implemenation"""
        # pass

    def check_token(self, token: str) -> dict:
        """Decodes the token to get the user id"""
        # To be implemented by the implementing class
        # if adding more implemenations need to define the output object structure with a schema
        return {}

    def check_role(self, user_id, role) -> bool:
        """Check if the user has given role"""
        # To be implemented by the implementing class
        return False

    def get_accessible_labels(self, user_id) -> [str]:
        """Check user rights and find document labels he can access"""
        # To be implemented by the implementing class
        return []

    def admin_auth_check_decorator(self, func):
        """For all data managment APIs"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract the access token from the request headers
            access_token = kwargs.get("token")
            if not access_token:
                raise ValueError("Access token is missing")
            user_data = self.check_token(access_token)
            if not self.check_role(user_data["user_id"], "admin"):
                raise PermissionException("Unauthorized access. User is not admin.")
            return await func(*args, **kwargs)

        return wrapper

    def chatbot_auth_check_decorator(self, func):
        """checks a predefined token in request header, and checks it is a
        valid, logged in, user.
        """

        @wraps(func)
        async def wrapper(websocket: WebSocket, *args, **kwargs):
            # Extract the access token from the request headers
            access_token = kwargs.get("token")
            if not access_token:
                raise ValueError("Access token is missing")
            try:
                self.check_token(access_token)
            except PermissionException:
                await websocket.accept()
                json_response = schema.BotResponse(
                    sender=schema.SenderType.BOT,
                    message="Please sign in first. I look forward to answering your questions.",
                    type=schema.ChatResponseType.ANSWER,
                    sources=[],
                    media=[],
                )
                await websocket.send_json({"logged_in": False, **json_response.dict()})
                return
            except Exception as exe:  # pylint: disable=broad-exception-caught
                log.exception(exe)
                await websocket.accept()
                json_response = schema.BotResponse(
                    sender=schema.SenderType.BOT,
                    message="Error in Authentication:" + str(exe),
                    type=schema.ChatResponseType.ANSWER,
                    sources=[],
                    media=[],
                )
                await websocket.send_json({"logged_in": False, **json_response.dict()})
                return
            return await func(websocket, *args, **kwargs)

        return wrapper

    def chatbot_get_labels_decorator(self, func):
        """checks a predefined token in request header, and returns available sources."""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract the access token from the request headers
            access_token = kwargs.get("token")
            if not access_token:
                db_labels = []
            else:
                try:
                    user_data = self.check_token(access_token)
                except Exception as exe:  # pylint: disable=broad-exception-caught
                    log.exception(exe)
                    db_labels = []
                else:
                    db_labels = self.get_accessible_labels(user_data["user_id"])
                    log.info(f"Accessible labels for the user: {db_labels=}")

            kwargs["labels"] = [
                label for label in kwargs["labels"] if label in db_labels
            ]
            # Proceed with the original function call and pass the sources to it
            return await func(*args, **kwargs)

        return wrapper
