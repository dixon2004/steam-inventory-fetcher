from utils.config import AUTH_TOKEN


class AuthorizationToken:

    def __init__(self):
        """
        Initialize Authorization Token.
        """
        self.auth_token = AUTH_TOKEN


    def check_auth_token(self, token) -> bool:
        """
        Check Authorization Token.
        
        Args:
            token (str): Authorization token.

        Returns:
            bool: True if token is valid, False otherwise.
        """
        if token != self.auth_token:
            return False
        
        return True
