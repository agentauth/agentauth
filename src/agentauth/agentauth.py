from datetime import datetime, timezone

from browser_use import Agent, Browser, BrowserConfig
from browser_use.controller.service import Controller

from agentauth import llm
from agentauth.credential_manager import CredentialManager
from agentauth.email_service import EmailService

class AgentAuth:
    def __init__(
            self,
            credentials_file: str = None,
            IMAP_SERVER: str = None,
            IMAP_PORT: int = 993,
            IMAP_USERNAME: str = None,
            IMAP_PASSWORD: str = None,
        ):
        self.credential_manager = CredentialManager()

        if credentials_file:
            self.credential_manager.load_json(credentials_file)

        self.email_service = None
        if IMAP_SERVER and IMAP_PORT and IMAP_USERNAME and IMAP_PASSWORD:
            self.email_service = EmailService(IMAP_SERVER, IMAP_PORT, IMAP_USERNAME, IMAP_PASSWORD)

        self.controller = Controller()
        self.controller.action("Look up the password")(self.lookup_password)
        self.controller.action("Look up the TOTP code")(self.lookup_totp)
        self.controller.action("Look up an email code")(self.lookup_email_code)
        self.controller.action("Look up an email link")(self.lookup_email_link)

        self.login_start_time = datetime.now(timezone.utc)

    async def auth(
        self,
        website: str,
        username: str,
        cdp_url: str = None
    ) -> dict:
        browser_config = BrowserConfig(
            cdp_url=cdp_url
        )
        browser = Browser(config=browser_config)
        browser_context = await browser.new_context()

        self.website = website
        self.username = username

        task, sensitive_data = self.build_auth_task(website, username)

        agent = Agent(
            task=task,
            llm=llm,
            sensitive_data=sensitive_data,
            browser=browser,
            browser_context=browser_context,
            controller=self.controller,
        )

        history = await agent.run()

        if not history.is_done():
            raise RuntimeError("Failed to authenticate")

        session = await browser_context.get_session()
        cookies =  await session.context.cookies()
        
        await browser_context.close()
        await browser.close()

        return cookies
    
    def build_auth_task(self, website: str, username: str) -> tuple[str, dict]:
        task_components = [f"""Navigate to "x_website" and log in with username "x_username". Use the following guidance:"""]
        sensitive_data = {
            "x_website": website,
            "x_username": username
        }

        try:
            password = self.lookup_password()
            task_components.append(f"""- If a password is needed, use the password "x_password" """)
            sensitive_data["x_password"] = password
        except LookupError:
            pass

        try:
            totp = self.lookup_totp()
            task_components.append("- If a TOTP code is needed,look up the TOTP code")
            sensitive_data["x_totp"] = totp
        except LookupError:
            pass

        if self.email_service:
            task_components.append("- If an email code is needed, look up the email code")
            task_components.append("- If an email link is needed, look up the email link and navigate to the link")
        
        # Prevent social sign in for now... may revist this later
        task_components.append("- Do not attempt to Sign in with Google.")
        task_components.append("- Do not attempt to Sign in with Apple.")
        task_components.append("- Do not attempt to Sign in with Facebook.")
        task_components.append("- Do not attempt to Sign in with Twitter.")
        task_components.append("- Do not attempt to Sign in with Microsoft.")
        task_components.append("- Do not attempt to Sign in with Amazon.")
        task_components.append("- Do not attempt to Sign in with LinkedIn.")
        task_components.append("- Do not attempt to Sign in with GitHub.")
        task_components.append("- Do not attempt to Sign in with SSO.")

        task_components.append("- Do not attempt to reset a password.")

        task = "\n".join(task_components)

        return task, sensitive_data
        
    def lookup_password(self) -> str:
        credential = self.credential_manager.get_credential(self.website, self.username)
        if credential and credential.password:
            return credential.password
        else:
            raise LookupError("No password found")
  
    def lookup_totp(self) -> str:
        credential = self.credential_manager.get_credential(self.website, self.username)
        if credential and credential.totp():
            return credential.totp()
        else:
            raise LookupError("No TOTP found")
    
    def lookup_email_code(self) -> str:
        code = self.email_service.get_code(self.login_start_time)
        if code:
            return code
        else:
            raise LookupError("No email code found")

    def lookup_email_link(self) -> str:
        code = self.email_service.get_link(self.login_start_time)
        if code:
            return code
        else:
            raise LookupError("No email link found")
