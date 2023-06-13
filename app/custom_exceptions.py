'''Definitions of different error classes and thier common names, messages, status code etc'''

class UnprocessableException(Exception):
    """Format for Unprocessable error"""
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Unprocessable Data"
        self.detail = detail
        self.status_code = 422

class PermissionException(Exception):
    '''Format for permission error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Permission Denied"
        self.detail = detail
        self.status_code = 403

class AccessException(Exception):
    '''Format for permission error'''
    def __init__(self, detail: str):
        super().__init__()
        self.name = "Access Denied"
        self.detail = detail
        self.status_code = 403

class OpenAIException(Exception):
    '''Format for errors from OpenAI APIs'''
    def __init__(self, detail):
        super().__init__()
        self.name = "Error from OpenAI"
        self.detail = detail
        self.status_code = 502
        