import pyotp
from urllib.parse import urlparse

class Credential:
    def __init__(self, website: str, username: str, password: str = None, totp_secret: str = None):
        self.website = website
        self.username = username
        self.password = password
        self.totp_secret = totp_secret

    def totp(self) -> str:
        if self.totp_secret:
            totp = pyotp.TOTP(self.totp_secret)
            return totp.now()
        return None
    
    def matches_website_and_username(self, website: str, username: str) -> bool:
        host1 = urlparse(self.website).netloc
        host2 = urlparse(website).netloc
        return host1 == host2 and self.username == username
