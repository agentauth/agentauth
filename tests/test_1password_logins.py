import asyncio
import os
import sys
from urllib.parse import urlparse

from agentauth import AgentAuth, CredentialManager
from browserbase import Browserbase
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv(override=True)

OP_SERVICE_ACCOUNT_TOKEN = os.getenv("OP_SERVICE_ACCOUNT_TOKEN")
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")

def get_browserbase_cdp_url():
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID, proxies=True)
    return session.connect_url

async def main():
    credential_manager = CredentialManager()
    await credential_manager.load_1password(OP_SERVICE_ACCOUNT_TOKEN)

    agentauth = AgentAuth(credential_manager=credential_manager)

    for credential in credential_manager.credentials:
        WEBSITE = credential.website
        USERNAME = credential.username

        cdp_url = get_browserbase_cdp_url()

        try:
            cookies = await agentauth.auth(WEBSITE, USERNAME, cdp_url=cdp_url)
        except Exception as e:
            print(f"Could not authenticate {WEBSITE} with {USERNAME}: {e}", file=sys.stderr)
            continue

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            
            # Add the authenticated cookies
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            await page.goto(WEBSITE)
            await page.wait_for_timeout(3000)

            # Save screenshot
            os.makedirs("screenshots", exist_ok=True)
            file_name = urlparse(WEBSITE).netloc.replace(".", "_")
            await page.screenshot(path=f"screenshots/{file_name}.png")

            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
