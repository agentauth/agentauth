import pyotp
from urllib.parse import urlparse

class Credential:
    """
    Credential represents a set of authentication credentials for a website.
    It stores the website URL, username, password, and optional TOTP secret.

    The class provides methods to generate TOTP codes and match credentials
    against a website/username pair.

    Args:
        website (str): The website URL these credentials are for
        username (str): The username or email for the account
        password (str, optional): The password for the account
        totp_secret (str, optional): The TOTP secret for generating 2FA codes
    """

    def __init__(self, website: str, username: str, password: str = None, totp_secret: str = None):
        """
        Initialize a new Credential object.

        Args:
            website (str): The website URL these credentials are for
            username (str): The username or email for the account
            password (str, optional): The password for the account
            totp_secret (str, optional): The TOTP secret for generating 2FA codes
        """
        self.website = website
        self.username = username
        self.password = password
        self.totp_secret = totp_secret

    def totp(self) -> str:
        """
        Generate the current TOTP code using the stored secret.

        Returns:
            str: The current TOTP code, or None if no TOTP secret is set

        Note:
            TOTP codes are time-based and typically valid for 30 seconds
        """
        if self.totp_secret:
            totp = pyotp.TOTP(self.totp_secret)
            return totp.now()
        return None
    
    def matches_website_and_username(self, website: str, username: str) -> bool:
        """
        Check if this credential matches a given website and username.

        The website matching is done by comparing the hostnames (domain names)
        rather than the exact URLs. This allows matching regardless of protocol
        (http vs https) and path.

        Args:
            website (str): The website URL to check against
            username (str): The username to check against

        Returns:
            bool: True if both the website domain and username match
        """
        host1 = urlparse(self.website).netloc
        host2 = urlparse(website).netloc
        return host1 == host2 and self.username == username
