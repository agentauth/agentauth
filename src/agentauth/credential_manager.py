import json
from typing import List

from agentauth.credential import Credential

class CredentialManager:
    def __init__(self):
        self.credentials: List[Credential] = []

    def load_json(self, file_path: str):
        new_credentials = []

        with open(file_path, 'r') as file:
            credentials_list = json.load(file)
            for x in credentials_list:
                credential = Credential(
                    website=x.get("website"),
                    username=x.get("username"),
                    password=x.get("password"),
                    totp_secret=x.get("totp_secret")
                )
                new_credentials.append(credential)
        
        self.credentials.extend(new_credentials)
        print(f"Loaded {len(new_credentials)} credentials from {file_path}")

    def load_1password(self):
        pass

    def load_bitwarden(self):
        pass

    def get_credential(self, website: str, username: str) -> Credential:
        for credential in self.credentials:
            if credential.matches_website_and_username(website, username):
                return credential
        return None
