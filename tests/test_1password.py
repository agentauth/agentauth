"""
Tests that AgentAuth can load credentials from 1Password.

- Requires OP_SERVICE_ACCOUNT_TOKEN to be set and have access to >= 1 login item
"""

import asyncio
import os

from dotenv import load_dotenv

from agentauth import AgentAuth

load_dotenv()

async def main():
    aa = AgentAuth(
        onepassword_service_account_token=os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
    )

    await aa.setup_credential_manager()

    assert len(aa.credential_manager.credentials) > 0

if __name__ == "__main__":
    asyncio.run(main())
