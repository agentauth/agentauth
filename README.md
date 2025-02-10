# AgentAuth

AgentAuth is a Python package that helps automate web authentication. It supports various authentication methods including email magic links, email verification codes, TOTP, and standard username/password login.

# Usage

```python
from agentauth import AgentAuth

aa = AgentAuth(
    credentials_file="credentials.json",
    IMAP_SERVER="imap.example.com",
    IMAP_USERNAME="agent@example.com",
    IMAP_PASSWORD="agent_email_password"
)

cookies = await aa.auth(
    "https://example.com",
    "agent@example.com",
    cdp_url="wss://..." # Optional, but services like Browserbase are helpful to avoid bot detection
)

# Use cookies for authenticated agent actions
```

# To Do

- [x] Look at package managers
- [x] Add license
- [x] Add example: browser-use
- [x] Add example: playwright
- [x] Add example: browserbase (cdp)
- [ ] Publish to pip
- [ ] Add 1Password integration
- [ ] Use local LLM for email scanning
- [ ] Allow other LLMs
