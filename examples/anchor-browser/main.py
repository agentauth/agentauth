import asyncio
import os

from agentauth import AgentAuth, CredentialManager
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

ANCHOR_API_KEY = os.getenv("ANCHOR_API_KEY")

async def main():
    # Use this URL to connect to Anchor Browser
    anchor_cdp_url = f"wss://connect.anchorbrowser.io?apiKey={ANCHOR_API_KEY}"

    # Create a new credential manager and load credentials file
    credential_manager = CredentialManager()
    credential_manager.load_json("credentials.json")

    # Initialize AgentAuth with a credential manager
    aa = AgentAuth(credential_manager=credential_manager)

    # Authenticate with a remote browser session; get the post-auth cookies
    cookies = await aa.auth(
        "https://practice.expandtesting.com/login",
        "practice",
        cdp_url=anchor_cdp_url
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
