from dotenv import load_dotenv
load_dotenv(override=True)

import asyncio
import json
import os

from agentauth import AgentAuth
from browserbase import Browserbase

def get_cdp_url():
    bb = Browserbase(api_key=os.getenv("BROWSERBASE_API_KEY"))
    session = bb.sessions.create(project_id=os.getenv("BROWSERBASE_PROJECT_ID"), proxies=True)
    return session.connect_url

async def main():
    aa = AgentAuth(
        credentials_file="credentials.json",
        IMAP_SERVER=os.getenv("IMAP_SERVER"),
        IMAP_USERNAME=os.getenv("IMAP_USERNAME"),
        IMAP_PASSWORD=os.getenv("IMAP_PASSWORD"),
    )

    auth1_cookies = await aa.auth(
        os.getenv("TEST_WEBSITE1"),
        os.getenv("TEST_USERNAME1"),
        # cdp_url=get_cdp_url()
    )

    auth2_cookies = await aa.auth(
        os.getenv("TEST_WEBSITE2"),
        os.getenv("TEST_USERNAME2"),
        # cdp_url=get_cdp_url()
    )

    print("\nAuth1 Cookies:")
    print(json.dumps(auth1_cookies, indent=2))

    print("\nAuth2 Cookies:")
    print(json.dumps(auth2_cookies, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
