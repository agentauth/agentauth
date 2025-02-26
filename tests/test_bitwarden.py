"""
Tests that AgentAuth can load credentials from Bitwarden.

- Requires BW_CLIENT_ID, BW_CLIENT_SECRET, and BW_MASTER_PASSWORD environment variables to be set
- Requires Bitwarden CLI to be installed and accessible in PATH
- Requires at least one login item in the Bitwarden vault
"""

import asyncio
import os

from dotenv import load_dotenv

from agentauth import CredentialManager

load_dotenv(override=True)

BW_CLIENT_ID = os.getenv("BW_CLIENT_ID")
BW_CLIENT_SECRET = os.getenv("BW_CLIENT_SECRET")
BW_MASTER_PASSWORD = os.getenv("BW_MASTER_PASSWORD")

async def main():
    # Create a new credential manager and load credentials file
    credential_manager = CredentialManager()
    credential_manager.load_bitwarden(
        BW_CLIENT_ID,
        BW_CLIENT_SECRET,
        BW_MASTER_PASSWORD
    )

    assert len(credential_manager.credentials) > 0

if __name__ == "__main__":
    asyncio.run(main())
