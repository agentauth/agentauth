import asyncio

from agentauth import AgentAuth, CredentialManager
from playwright.async_api import async_playwright

async def main():
    # Create a new credential manager and load credentials file
    credential_manager = CredentialManager()
    credential_manager.load_json("credentials.json")

    # Initialize AgentAuth with a credential manager
    aa = AgentAuth(credential_manager=credential_manager)

    # Authenticate and get the post-auth cookies
    cookies = await aa.auth(
        "https://practice.expandtesting.com/login",
        "practice"
    )

    # Take some authenticated action(s) using the cookies
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)

        # Create a new page and add the cookies from AgentAuth
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
