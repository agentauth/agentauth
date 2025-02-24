import asyncio
import os

from agentauth import AgentAuth, CredentialManager
from browserbase import Browserbase
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv(override=True)

BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")

def get_browserbase_cdp_url():
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID)
    return session.connect_url

async def main():
    browserbase_cdp_url = get_browserbase_cdp_url()

    # Create a new credential manager and load credentials file
    credential_manager = CredentialManager()
    credential_manager.load_json("credentials.json")

    # Initialize AgentAuth with a credential manager
    aa = AgentAuth(credential_manager=credential_manager)

    # Authenticate with a remote browser session; get the post-auth cookies
    cookies = await aa.auth(
        "https://practice.expandtesting.com/login",
        "practice",
        cdp_url=browserbase_cdp_url
    )

    # Load cookies into a new browser and load an authenticated page
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Add the authenticated cookies
        await context.add_cookies(cookies)
        
        page = await context.new_page()
        await page.goto("https://practice.expandtesting.com/secure")
        
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
