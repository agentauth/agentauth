import asyncio
from urllib.parse import urlparse
import os

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

    test_results = {}

    for credential in credential_manager.credentials:
        WEBSITE = credential.website
        USERNAME = credential.username

        cdp_url = get_browserbase_cdp_url()

        try:
            cookies = await agentauth.auth(WEBSITE, USERNAME, cdp_url=cdp_url)
        except Exception as e:
            print(f"Could not authenticate {WEBSITE} with {USERNAME}: {e}")
            test_results[WEBSITE] = {
                "username": USERNAME,
                "status": "❌ Failed",
                "screenshot": "",
            }
            continue

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            context = await browser.new_context()
            
            # Add the authenticated cookies
            await context.add_cookies(cookies)
            
            page = await context.new_page()
            await page.goto(WEBSITE)
            await page.wait_for_timeout(3000)

            # Save screenshot
            os.makedirs("screenshots", exist_ok=True)
            file_name = f"screenshots/{urlparse(WEBSITE).netloc}_{os.urandom(4).hex()}.png"
            await page.screenshot(path=file_name)

            test_results[WEBSITE] = {
                "username": USERNAME,
                "status": "✅ Success",
                "screenshot": file_name,
            }

            await browser.close()

    # Print test results as table
    print("\nTest Results:")
    print("-" * 100)
    print(f"{'Website':<30} {'Username':<20} {'Status':<10} {'Screenshot'}")
    print("-" * 100)
    for website, result in test_results.items():
        print(f"{website[:30]:<30} {result['username'][:20]:<20} {result['status']:<10} {result['screenshot']}")
    print("-" * 100)

if __name__ == "__main__":
    asyncio.run(main())
