import asyncio
import os

from agentauth import AgentAuth
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv(override=True)

# Environment variables
IMAP_SERVER = os.getenv('IMAP_SERVER')
IMAP_USERNAME = os.getenv('IMAP_USERNAME')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
MAGIC_LINK_TEST_WEBSITE = os.getenv("MAGIC_LINK_TEST_WEBSITE")
MAGIC_LINK_TEST_AUTHENTICATED_PAGE = os.getenv("MAGIC_LINK_TEST_AUTHENTICATED_PAGE")
MAGIC_LINK_TEST_USERNAME = os.getenv("MAGIC_LINK_TEST_USERNAME")
async def main():
    aa = AgentAuth(
        imap_server=IMAP_SERVER,
        imap_username=IMAP_USERNAME,
        imap_password=IMAP_PASSWORD
    )

    cookies = await aa.auth(
        MAGIC_LINK_TEST_WEBSITE,
        MAGIC_LINK_TEST_USERNAME
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Load the cookies into the browser context
        for cookie in cookies:
            await context.add_cookies([cookie])

        # Navigate to the website to verify cookies worked
        page = await context.new_page()
        await page.goto(MAGIC_LINK_TEST_AUTHENTICATED_PAGE)
        await page.wait_for_timeout(10000)
        
        await browser.close()

    assert len(cookies) > 0

if __name__ == "__main__":
    asyncio.run(main())
