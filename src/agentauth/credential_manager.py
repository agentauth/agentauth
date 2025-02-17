import json
from typing import List

from onepassword.client import Client

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

    async def load_1password(self, service_account_token: str):
        client = await Client.authenticate(
            auth=service_account_token,
            integration_name="1Password Integration",
            integration_version="v0.1.0"
        )

        new_credentials = []

        # Loop over all vaults
        vaults = await client.vaults.list_all()
        async for vault in vaults:
            # Loop over all items in the vault
            items = await client.items.list_all(vault.id)
            async for item in items:
                # Loop over all websites for the item
                for website in item.websites:
                    url = website.url

                    # If there is no username or password, do not create a credential
                    try:
                        username = await client.secrets.resolve(f"op://{item.vault_id}/{item.id}/username")
                        password = await client.secrets.resolve(f"op://{item.vault_id}/{item.id}/password")
                    except:
                        continue

                    # Add TOTP secret if it exists, but it is optional
                    totp_secret = ""
                    try:
                        totp_secret = await client.secrets.resolve(f"op://{item.vault_id}/{item.id}/totpsecret")
                    except:
                        pass

                    credential = Credential(
                        website=url,
                        username=username,
                        password=password,
                        totp_secret=totp_secret
                    )
                    new_credentials.append(credential)

        self.credentials.extend(new_credentials)
        print(f"Loaded {len(new_credentials)} credentials from 1Password")

    def get_credential(self, website: str, username: str) -> Credential:
        for credential in self.credentials:
            if credential.matches_website_and_username(website, username):
                return credential
        return None
