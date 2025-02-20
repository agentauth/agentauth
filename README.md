# AgentAuth

AgentAuth is a Python package that helps automate web authentication by simulating human-like login behavior. It supports various authentication methods including:
- Email magic links
- Email verification codes
- Time-based One-Time Passwords (TOTP)
- Standard username/password login

## Features

- 🤖 **Automated Authentication**: Handles complex login flows automatically
- 📧 **Email Integration**: Supports email-based verification (magic links and codes)
- 🔐 **Password Manager Integration**: Works with 1Password and local credential storage
- 🌐 **Browser Integration**: Compatible with remote CDP-based browsers

## Installation

```bash
pip install agentauth
```

## Quick Start

```python
from agentauth import AgentAuth, CredentialManager

# Initialize credential manager and load credentials
credential_manager = CredentialManager()
credential_manager.load_file("credentials.json")  # Load from local JSON file

aa = AgentAuth(
    credential_manager=credential_manager,

    # Connect an email inbox for authentication requiring email links or codes
    imap_server="imap.example.com",
    imap_username="agent@example.com",
    imap_password="agent_email_password"
)

# Authenticate to a website for a given username
cookies = await aa.auth(
    "https://example.com",
    "agent@example.com",
    cdp_url="wss://..."  # Optional: for using remote browser services
)

# Use cookies for authenticated agent actions
```

# To Do

- [ ] Add audit logging
- [ ] Add Bitwarden integration
- [ ] Use local LLM for email scanning
- [ ] Allow other LLMs

# Contributing

Contributions are welcome! Please feel free to submit a pull request.

# License

This project is licensed under the MIT License.
