import asyncio
import tempfile

from agentauth import AgentAuth
from browser_use import Agent, Browser
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from langchain_openai import ChatOpenAI

async def main():
    # Initialize AgentAuth with credentials file
    aa = AgentAuth(
        credentials_file="credentials.json"
    )

    # Create a temp file to store the cookies
    cookies_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json')
    cookies_file_name = cookies_file.name

    # Authenticate for a specific website and user; get the session cookies
    await aa.auth(
        "https://opensource-demo.orangehrmlive.com",
        "Admin",
        cookies_file=cookies_file_name
    )

    # Use browser-use to take some post-login action(s)
    context = BrowserContext(
        browser=Browser(),
        config=BrowserContextConfig(cookies_file=cookies_file_name)
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
