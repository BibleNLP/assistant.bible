import os
from supabase import create_client, Client
import gotrue.errors

from core.auth import AuthInterface
from custom_exceptions import SupabaseException, GenericException, PermissionException

class Supabase(AuthInterface):
    '''The supabase implementation of the auth interface'''
    def __init__(self,
                url=os.environ.get("SUPABASE_URL"),
                key=os.environ.get("SUPABASE_KEY")):
        '''Connect to Supabase server'''
        self.conn = create_client(url, key)

    def check_token(self, access_token):
        '''Pass on the token from user to supabase and get id'''
        try:
            access_token_str = access_token.get_secret_value()
            # Verify the access token using Supabase secret
            user_data = self.conn.auth.get_user(access_token_str)
        except gotrue.errors.AuthApiError as exe:
            raise PermissionException("Unauthorized access. Invalid token.") from exe
        except Exception as exe:
            raise SupabaseException(str(exe)) from exe
        return user_data.__dict__

    def check_role(self, user_id, role='admin'):
        '''Check supabase DB tables to see if user is the given role.'''
        if role != "admin":
            raise GenericException("Different roles is not supported in Supabase (yet)!!!")
        result = self.conn.table('adminUsers').select('''
                        user_id
                        '''
                    ).eq(
                    'user_id', user_id
                    ).execute()
        if result:
            return True
        return False

    def get_accessible_labels(self, user_id):
        '''Queries the supabase table to bet user-source mapping'''
        result = self.conn.table('userAttributes').select(
            'id, user_id, user_type, "userTypes"(user_type, sources)').eq(
            'user_id', user_id).execute()
        db_labels = []
        for data in result.data:
            db_labels.extend(data.get('userTypes', {}).get('sources', []))
        return db_labels
