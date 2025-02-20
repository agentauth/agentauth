from datetime import datetime, timezone
import logging

from browser_use import Agent, Browser, BrowserConfig
from browser_use.controller.service import Controller

from agentauth import llm
from agentauth.credential_manager import CredentialManager
from agentauth.email_service import EmailService

class AgentAuth:
    """
    AgentAuth is the main class for handling automated web authentication.
    It supports various authentication methods including username/password,
    TOTP, email magic links, and email verification codes.

    The class uses browser automation and LLMs to understand and navigate
    login forms in a human-like manner.

    Args:
        credential_manager (CredentialManager, optional): Manager for handling credentials.
            If not provided, a new empty manager will be created.
        imap_server (str, optional): IMAP server for email verification.
            Required for magic links and verification codes.
        imap_port (int, optional): IMAP port number. Defaults to 993.
        imap_username (str, optional): Email username for IMAP.
            Required if imap_server is provided.
        imap_password (str, optional): Email password for IMAP.
            Required if imap_server is provided.
    """

    def __init__(
            self,
            credential_manager: CredentialManager = None,
            imap_server: str = None,
            imap_port: int = 993,
            imap_username: str = None,
            imap_password: str = None,
        ):
        self.credential_manager = credential_manager or CredentialManager()
        
        self.email_service = None
        if imap_server and imap_port and imap_username and imap_password:
            self.email_service = EmailService(imap_server, imap_port, imap_username, imap_password)

        self.controller = Controller()
        self.controller.action("Look up the password")(self.lookup_password)
        self.controller.action("Look up the TOTP code")(self.lookup_totp)
        self.controller.action("Look up an email code")(self.lookup_email_code)
        self.controller.action("Look up an email link")(self.lookup_email_link)

        self.login_start_time = datetime.now(timezone.utc)

        self._setup_logging()

    def _setup_logging(self):
        browser_use_logger = logging.getLogger("browser_use")
        browser_use_logger.handlers.clear()
        file_handler = logging.FileHandler('agentauth.log')
        browser_use_logger.addHandler(file_handler)
        browser_use_logger.propagate = False

    async def auth(
        self,
        website: str,
        username: str,
        cdp_url: str = None,
        headless: bool = True,
    ) -> dict:
        """
        Performs automated authentication on the specified website.

        This method will:
        1. Launch a browser (local or remote)
        2. Navigate to the website
        3. Attempt to log in using available credentials
        4. Handle any additional verification steps (TOTP, email verification)
        5. Return the authenticated session cookies

        Args:
            website (str): The URL of the website to authenticate with
            username (str): The username to authenticate with
            cdp_url (str, optional): CDP URL for remote browser service.
                Recommended for production to avoid bot detection.
            headless (bool, optional): Whether to run the browser in headless mode.
                Defaults to True. Set to False for debugging.

        Returns:
            dict: Session cookies from the authenticated browser session

        Raises:
            RuntimeError: If authentication fails
            LookupError: If required credentials are not found
        """
        browser_config = BrowserConfig(
            headless=headless,
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
