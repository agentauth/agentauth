import json
from typing import List

from onepassword.client import Client

from agentauth.credential import Credential

class CredentialManager:
    """
    CredentialManager handles the storage and retrieval of authentication credentials.
    It supports loading credentials from local JSON files and 1Password.

    The manager maintains an in-memory list of credentials that can be loaded
    from multiple sources. Each credential contains website, username, password,
    and optional TOTP information.

    Example:
        ```python
        manager = CredentialManager()
        
        # Load from JSON file
        manager.load_json("credentials.json")
        
        # Load from 1Password
        await manager.load_1password("your_1password_token")
        
        # Get credentials for a site
        cred = manager.get_credential("https://example.com", "user@example.com")
        ```
    """

    def __init__(self):
        """
        Initialize a new CredentialManager with an empty credential list.
        """
        self.credentials: List[Credential] = []

    def load_json(self, file_path: str):
        """
        Load credentials from a JSON file.

        The JSON file should contain an array of credential objects, each with:
        - website: The website URL
        - username: The username or email
        - password: The password
        - totp_secret: (optional) TOTP secret for 2FA

        Args:
            file_path (str): Path to the JSON credentials file

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
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
        """
        Load credentials from a 1Password account using the Connect server API.

        This method will:
        1. Authenticate with 1Password using the service account token
        2. Iterate through all vaults
        3. Extract login items with usernames and passwords
        4. Optionally extract TOTP secrets if available

        Args:
            service_account_token (str): 1Password Connect server API token

        Raises:
            RuntimeError: If authentication fails
            Exception: If credential extraction fails
        """
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
        """
        Retrieve credentials for a specific website and username combination.

        Args:
            website (str): The website URL to find credentials for
            username (str): The username to find credentials for

        Returns:
            Credential: The matching credential object, or None if not found
        """
        for credential in self.credentials:
            if credential.matches_website_and_username(website, username):
                return credential
        return None
