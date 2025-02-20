# Default to an OpenAI model. Note this requires the OPENAI_API_KEY environment variable.
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", temperature=0)


from agentauth.agentauth import AgentAuth
from agentauth.credential_manager import CredentialManager
from agentauth.credential import Credential

__all__ = ["AgentAuth", "CredentialManager", "Credential"]
