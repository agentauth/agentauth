# Default to an OpenAI model. Note this requires the OPENAI_API_KEY environment variable.
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", temperature=0)

import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)
logger = structlog.get_logger("agentauth")

from agentauth.agentauth import AgentAuth
from agentauth.credential_manager import CredentialManager
from agentauth.credential import Credential

__all__ = ["AgentAuth", "CredentialManager", "Credential"]
