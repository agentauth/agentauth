import asyncio
import os

from agentauth import AgentAuth
from browserbase import Browserbase
from playwright.async_api import async_playwright

BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")

def get_browserbase_session():
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID)
    return session

async def main():
    # Initialize AgentAuth with credentials file
    aa = AgentAuth(
        credentials_file="credentials.json"
    )

    # Authenticate with a remote browser session; get the post-auth cookies
    browserbase_session = get_browserbase_session()
    cookies = await aa.auth(
        "https://practice.expandtesting.com/login",
        "practice",
        cdp_url=browserbase_session.connect_url
    )

    # Take some authenticated action(s) using the cookies
    browserbase_session = get_browserbase_session()
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(browserbase_session.connect_url)

        page = await browser.new_page()
        await page.context.add_cookies(cookies)
        await page.goto("https://practice.expandtesting.com/secure")

        # Check if we were redirected to the login page. If not, we should be logged in.
        if page.url == "https://practice.expandtesting.com/login":
            print("Not signed in...")
        else:
            element = page.locator('#username')
            text = await element.text_content()
            print(f"Page message: {text.strip()}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
