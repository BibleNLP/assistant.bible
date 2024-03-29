"""
This module contains the Supabase class which implements the AuthInterface. 
It provides methods to interact with the Supabase server for authentication purposes.
"""
import os
from supabase import create_client
import gotrue.errors

from core.auth import AuthInterface
from custom_exceptions import SupabaseException, GenericException, PermissionException


# pylint: disable=fixme
class Supabase(AuthInterface):
    """The supabase implementation of the auth interface"""

    def __init__(
        self, url=os.environ.get("SUPABASE_URL"), key=os.environ.get("SUPABASE_KEY")
    ):
        """Connect to Supabase server"""
        self.conn = create_client(url, key)

    def check_token(self, token):
        """Pass on the token from user to supabase and get id"""
        try:
            access_token_str = token.get_secret_value()
            # Verify the access token using Supabase secret
            user_data = self.conn.auth.get_user(access_token_str)
        except gotrue.errors.AuthApiError as exe:
            raise PermissionException(
                "Unauthorized access. Invalid token.") from exe
        except Exception as exe:  # pylint: disable=broad-exception-caught
            raise SupabaseException(str(exe)) from exe
        return {"user_id": user_data.user.id, "user_roles": [], "user_name": ""}

    def check_role(self, user_id, role="admin"):
        """Check supabase DB tables to see if user is the given role."""
        if role != "admin":
            raise GenericException(
                "Different roles is not supported in Supabase (yet)!!!"
            )
        try:
            result = (
                self.conn.table("adminUsers")
                .select(
                    """
                            user_id
                            """
                )
                .eq("user_id", user_id)
                .execute()
            )
        except Exception as exe:  # pylint: disable=broad-exception-caught
            raise SupabaseException(str(exe)) from exe
        if result:
            return True
        return False

    def get_accessible_labels(self, user_id):
        """Queries the supabase table to get user-source mapping"""
        try:
            result = (
                self.conn.table("userAttributes")
                .select('id, user_id, user_type, "userTypes"(user_type, sources)')
                .eq("user_id", user_id)
                .execute()
            )
        except Exception as exe:
            raise SupabaseException(str(exe)) from exe
        db_labels = []
        for data in result.data:
            db_labels.extend(data.get("userTypes", {}).get("sources", []))
        return db_labels
