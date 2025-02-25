from datetime import datetime, timezone
import logging
import os

from browser_use import Agent, Browser, BrowserConfig
from browser_use.controller.service import Controller
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from agentauth import logger
from agentauth.credential_manager import CredentialManager
from agentauth.email_service import EmailService
from agentauth.id_generator import generate_id

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
            llm: BaseChatModel = None,
            imap_server: str = None,
            imap_port: int = 993,
            imap_username: str = None,
            imap_password: str = None,
            agent_id: str = None,
        ):
        self.credential_manager = credential_manager or CredentialManager()
        
        if not llm and not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY environment variable not set. Please set this variable or provide a custom LLM with the `llm` parameter.")
        
        self.llm = llm or ChatOpenAI(model="gpt-4o", temperature=0.0)

        self.email_service = None
        if imap_server and imap_port and imap_username and imap_password:
            self.email_service = EmailService(imap_server, imap_port, imap_username, imap_password, self.llm)

        self.agent_id = agent_id or generate_id()

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
        self.website = website
        self.username = username
        self.log_auth_event("started login attempt")

        browser_config = BrowserConfig(
            headless=headless,
            cdp_url=cdp_url
        )
        browser = Browser(config=browser_config)
        browser_context = await browser.new_context()

        self.controller = Controller()
        task, sensitive_data = self.build_auth_task(website, username)

        agent = Agent(
            task=task,
            llm=self.llm,
            sensitive_data=sensitive_data,
            browser=browser,
            browser_context=browser_context,
            controller=self.controller,
        )
        
        history = await agent.run()

        if not history.is_done():
            raise RuntimeError("Failed to authenticate")
        
        self.log_auth_event("authentication successful")

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

        if self._can_lookup_password():
            password = self.lookup_password()
            sensitive_data["x_password"] = password
            task_components.append(f"""- If a password is needed, use the password "x_password" """)

        if self._can_lookup_totp():
            self.controller.action("Look up the TOTP code")(self.lookup_totp)
            task_components.append("- If a TOTP code is needed, look up the TOTP code")

        if self._can_lookup_email_code():
            self.controller.action("Look up the email code")(self.lookup_email_code)
            task_components.append("- If an email code is needed, look up the email code")

        if self._can_lookup_email_link():
            self.controller.action("Look up the email link")(self.lookup_email_link)
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
    
    def _can_lookup_password(self) -> bool:
        return bool(
            self.credential_manager and 
            self.credential_manager.get_credential(self.website, self.username) and
            self.credential_manager.get_credential(self.website, self.username).password
        )

    def lookup_password(self) -> str:
        if not self._can_lookup_password():
            raise LookupError("Cannot lookup password")
        
        password = self.credential_manager.get_credential(self.website, self.username).password
        self.log_auth_event("retrieved password")
        return password
  
    def _can_lookup_totp(self) -> bool:
        return bool(
            self.credential_manager and 
            self.credential_manager.get_credential(self.website, self.username) and
            self.credential_manager.get_credential(self.website, self.username).totp()
        )

    def lookup_totp(self) -> str:
        if not self._can_lookup_totp():
            raise LookupError("Cannot lookup TOTP")

        totp = self.credential_manager.get_credential(self.website, self.username).totp()
        self.log_auth_event("retrieved TOTP")
        return totp
    
    def _can_lookup_email_code(self) -> bool:
        return bool(self.email_service)

    def lookup_email_code(self) -> str:
        if not self._can_lookup_email_code():
            raise LookupError("Cannot lookup email code")

        code = self.email_service.get_code(self.login_start_time)
        self.log_auth_event("retreived email code", imap_username=self.email_service.imap_username)
        return code

    def _can_lookup_email_link(self) -> bool:
        return bool(self.email_service)

    def lookup_email_link(self) -> str:
        if not self._can_lookup_email_link():
            raise LookupError("Cannot lookup email link")

        link = self.email_service.get_link(self.login_start_time)
        self.log_auth_event("retreived email link", imap_username=self.email_service.imap_username)
        return link
    
    def log_auth_event(self, event: str, **kwargs):
        logger.info(
            event,
            agent_id=self.agent_id,
            website=self.website,
            username=self.username,
            **kwargs
        )
