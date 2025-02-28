import json
import os
import re
import subprocess
from typing import List

from onepassword.client import Client

from agentauth import logger
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
                        totp_secret = await client.secrets.resolve(f"op://{item.vault_id}/{item.id}/one-time password")
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
        logger.info("loaded credential(s) from 1Password", count=len(new_credentials))

    def load_bitwarden(self, client_id: str, client_secret: str, master_password: str):
        """
        Load credentials from Bitwarden.

        This method uses the Bitwarden CLI to authenticate and retrieve credentials. It requires the
        Bitwarden CLI to be installed and accessible in the system PATH.

        Args:
            client_id (str): Bitwarden API client ID
            client_secret (str): Bitwarden API client secret 
            master_password (str): Master password for unlocking the Bitwarden vault

        Raises:
            RuntimeError: If Bitwarden CLI is not found or authentication fails
            Exception: If credential extraction fails
        """
        test_process = subprocess.run(['bw', '--version'], capture_output=True)
        if test_process.returncode != 0:
            raise RuntimeError("Bitwarden CLI not found")

        # Login to Bitwarden and unlock in one command
        unlock_process = subprocess.run(
            'bw login --apikey; bw sync; bw unlock --passwordenv BW_MASTER_PASSWORD',
            shell=True,
            capture_output=True,
            text=True,
            env={
                'BW_CLIENTID': client_id,
                'BW_CLIENTSECRET': client_secret,
                'BW_MASTER_PASSWORD': master_password,
                'PATH': os.environ['PATH']
            }
        )
        if unlock_process.returncode != 0:
            raise RuntimeError("Failed to login or unlock Bitwarden:", unlock_process.stderr)

        # Extract session key
        session_match = re.search(r'BW_SESSION="([^"]+)"', unlock_process.stdout)
        if not session_match:
            raise RuntimeError("Failed to retrieve session key from Bitwarden")
        session_key = session_match.group(1)

        # List all items using the session key
        list_process = subprocess.run(
            ['bw', 'list', 'items'], 
            capture_output=True, 
            text=True,
            env={
                'BW_SESSION': session_key,
                'PATH': os.environ['PATH']
            }
        )
        if list_process.returncode != 0:
            raise RuntimeError("Failed to get items from Bitwarden:", list_process.stderr)

        # Parse and process the items
        items = json.loads(list_process.stdout)
        new_credentials = []

        for item in items:
            # Skip items that don't have login information
            if not item.get('login'):
                continue
            
            login = item['login']
            
            # Get all URIs from the login
            for uri_item in login.get('uris', []):
                uri = uri_item.get('uri')
                credential = Credential(
                    website=uri,
                    username=login.get('username'),
                    password=login.get('password'),
                    totp_secret=login.get('totp')
                )
                new_credentials.append(credential)

        self.credentials.extend(new_credentials)
        logger.info("loaded credential(s) from Bitwarden", count=len(new_credentials))

    def load_credential(self, credential_dict: dict):
        """
        Load a single credential from a dictionary.

        Args:
            credential_dict (dict): Dictionary containing credential information with keys:
                - website: The website URL (required)
                - username: The username or email (required)
                - password: The password (required)
                - totp_secret: TOTP secret for 2FA (optional)
        """
        credential = Credential(
            website=credential_dict.get('website'),
            username=credential_dict.get('username'),
            password=credential_dict.get('password'),
            totp_secret=credential_dict.get('totp_secret')
        )
        self.credentials.append(credential)
        logger.info("loaded credential", count=1)

    def load_credentials(self, credential_list: List[dict]):
        """
        Load credentials from a list of dictionaries.

        Args:
            credential_list (List[dict]): List of dictionaries, each containing credential information with keys:
                - website: The website URL (required)
                - username: The username or email (required)
                - password: The password (required)
                - totp_secret: TOTP secret for 2FA (optional)
        """
        new_credentials = []
        for credential_dict in credential_list:
            credential = Credential(
                website=credential_dict.get('website'),
                username=credential_dict.get('username'),
                password=credential_dict.get('password'),
                totp_secret=credential_dict.get('totp_secret')
            )
            new_credentials.append(credential)
        
        self.credentials.extend(new_credentials)
        logger.info("loaded credential(s) from list", count=len(new_credentials))

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
        logger.info("loaded credential(s) from JSON file", file_path=file_path, count=len(new_credentials))

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
