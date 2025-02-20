import asyncio
import json
import tempfile

from agentauth import AgentAuth, CredentialManager
from browser_use import Agent, Browser
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from langchain_openai import ChatOpenAI

async def main():
    # Create a new credential manager and load credentials file
    credential_manager = CredentialManager()
    credential_manager.load_json("credentials.json")

    # Initialize AgentAuth with a credential manager
    aa = AgentAuth(credential_manager=credential_manager)

    # Authenticate for a specific website and user; get the session cookies
    cookies = await aa.auth(
        "https://opensource-demo.orangehrmlive.com",
        "Admin"
    )

    # Write the cookies to a temp file
    cookies_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json')
    with open(cookies_file.name, 'w') as f:
        json.dump(cookies, f, indent=2)

    # Use browser-use to take some post-login action(s)
    context = BrowserContext(
        browser=Browser(),
        config=BrowserContextConfig(cookies_file=cookies_file.name)
    )
    agent = Agent(
        task="Go to opensource-demo.orangehrmlive.com and update my nickname to be a random silly nickname",
        llm=ChatOpenAI(model="gpt-4o"),
        browser_context=context
    )

    # Run the browser-use agent
    await agent.run()

    # Clean up: delete cookies file and close the browser
    cookies_file.close()
    await context.close()

if __name__ == "__main__":
    asyncio.run(main())
