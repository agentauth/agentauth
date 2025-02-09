from langchain_openai import ChatOpenAI

# Default to an OpenAI model. Note this requires the OPENAI_API_KEY environment variable.
llm = ChatOpenAI(model="gpt-4o", temperature=0)

from agentauth.agentauth import AgentAuth

__all__ = ["AgentAuth"]
