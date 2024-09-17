from utils.config import AUTH_TOKEN
from fastapi import HTTPException
from utils.log import write_log
import secrets


class AuthorizationToken:

    def __init__(self):
        """
        Initialize Authorization Token.
        """
        self.auth_token = self.get_auth_token()


    def get_auth_token(self):
        try:
            if not AUTH_TOKEN:
                write_log("error", "[AuthorizationToken] Authorization token is not set.")
                return self.generate_auth_token()
            else:
                return AUTH_TOKEN
        except Exception as e:
            write_log("error", f"[AuthorizationToken] Failed to get authorization token: {e}")


    def generate_auth_token(self) -> str:
        """
        Generate Authorization Token.
        
        Returns:
            str: Authorization token.
        """
        try:
            write_log("info", "[AuthorizationToken] Generating new authorization token.")
            auth_token = secrets.token_urlsafe(32)
            write_log("info", f"[AuthorizationToken] New authorization token: {auth_token}")
            return auth_token
        except Exception as e:
            write_log("error", f"[AuthorizationToken] Failed to generate authorization token: {e}")


    def check_auth_token(self, token) -> None:
        """
        Check Authorization Token.
        
        Args:
            token (str): Authorization token.
        """
        if token != self.auth_token:
            raise HTTPException(status_code=401, detail="Unauthorized.")
        