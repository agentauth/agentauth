"""
Tests that AgentAuth can load credentials from 1Password.

- Requires OP_SERVICE_ACCOUNT_TOKEN to be set and have access to >= 1 login item
"""

import asyncio
import os

from dotenv import load_dotenv

from agentauth import AgentAuth, CredentialManager

load_dotenv(override=True)

async def main():
    # Create a new credential manager and load credentials file
    credential_manager = CredentialManager()
    await credential_manager.load_1password(os.getenv("OP_SERVICE_ACCOUNT_TOKEN"))

    assert len(credential_manager.credentials) > 0

if __name__ == "__main__":
    asyncio.run(main())
