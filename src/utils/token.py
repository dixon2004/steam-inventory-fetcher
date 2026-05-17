from utils.config import AUTH_TOKEN


class AuthorizationToken:

    def __init__(self):
        """
        Initializes the AuthorizationToken with the predefined authentication token from the configuration.
        """
        self.auth_token = AUTH_TOKEN


    def check_auth_token(self, token: str) -> bool:
        """
        Checks if the provided token matches the predefined authentication token.

        Args:
            token (str): The token to be checked against the predefined authentication token.

        Returns:
            bool: True if the provided token matches the predefined authentication token, False otherwise.
        """
        return token == self.auth_token
