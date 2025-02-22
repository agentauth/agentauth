import asyncio
import os

from dotenv import load_dotenv

from agentauth import AgentAuth, CredentialManager

load_dotenv(override=True)

async def main():
    credential_manager = CredentialManager()
    await credential_manager.load_1password(os.getenv("OP_SERVICE_ACCOUNT_TOKEN"))

    aa = AgentAuth(credential_manager=credential_manager)

    cookies = await aa.auth(
        os.getenv("PASSWORD_TOTP_TEST_WEBSITE"),
        os.getenv("PASSWORD_TOTP_TEST_USERNAME"),
        headless=False
    )

    assert len(cookies) > 0

if __name__ == "__main__":
    asyncio.run(main())
