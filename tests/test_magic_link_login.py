import asyncio
import os

from dotenv import load_dotenv

from agentauth import AgentAuth

load_dotenv(override=True)

async def main():
    aa = AgentAuth(
        imap_server=os.getenv('IMAP_SERVER'),
        imap_username=os.getenv('IMAP_USERNAME'),
        imap_password=os.getenv('IMAP_PASSWORD')
    )

    cookies = await aa.auth(
        os.getenv("MAGIC_LINK_TEST_WEBSITE"),
        os.getenv("MAGIC_LINK_TEST_USERNAME")
    )

    assert len(cookies) > 0

if __name__ == "__main__":
    asyncio.run(main())
