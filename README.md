# AgentAuth

AgentAuth is a Python package that helps automate web authentication by simulating human-like login behavior. It supports various authentication methods including:
- Standard username/password login
- Time-based One-Time Passwords (TOTP)
- Email magic links
- Email verification codes

## Features

- 🤖 **Automated Authentication**: Handles complex login flows automatically
- 📧 **Email Integration**: Supports email-based verification (magic links and codes)
- 🔐 **Password Manager Integration**: Works with 1Password, Bitwarden, and local credential storage
- 🌐 **Browser Integration**: Compatible with remote CDP-based browsers

## Installation

```bash
pip install agentauth
```

## Quick Start

```python
from agentauth import AgentAuth, CredentialManager

# Add credentials to a new credential manager
credential_manager = CredentialManager()
credential_manager.load_credential({
    "website": "https://www.example.com",
    "username": "user@example.com",
    "password": "user_password"
})

# Create an instance of AgentAuth with access to credentials
aa = AgentAuth(credential_manager=credential_manager)

# Authenticate to a website for a given username
cookies = await aa.auth("https://www.example.com", "user@example.com")

# User is logged in! 🎉
# Use cookies for authenticated agent actions... (see examples directory to see how)
```

**ℹ️ You can pass a custom LLM to the AgentAuth constructor. OpenAI's `gpt-4o` is the default and requires an `OPENAI_API_KEY` environment variable.**

## Connecting an email inbox

Many websites require an email step to authenticate. This could be for a magic link or login code, or it could be for email-based two-factor authentication. AgentAuth supports connecting an email inbox to handle these cases.

```python
aa = AgentAuth(
    imap_server="imap.example.com",
    imap_username="agent@example.com",
    imap_password="agent_email_password"
)

cookies = await aa.auth("https://www.example.com", "agent@example.com")
```

## Loading credentials from various sources

```python
from agentauth import AgentAuth, CredentialManager

# Create a new credential manager
credential_manager = CredentialManager()

# Load credentials from 1Password
credential_manager.load_1password(os.getenv("OP_SERVICE_ACCOUNT_TOKEN"))

# Load credentials from Bitwarden
credential_manager.load_bitwarden(
    os.getenv("BW_CLIENT_ID"),
    os.getenv("BW_CLIENT_SECRET"),
    os.getenv("BW_MASTER_PASSWORD")
)

# Load credentials from a file
credential_manager.load_file("credentials.json")

# Load a single credential
credential_manager.load_credential({
    "website": "https://www.example.com",
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD")
})

# Load a list of credentials
credential_manager.load_credentials([
    {
        "website": "https://www.example.com",
        "username": os.getenv("EXAMPLE_USERNAME"),
        "password": os.getenv("EXAMPLE_PASSWORD")
    },
    {
        "website": "https://www.fakewebsite.com",
        "username": os.getenv("FAKEWEBSITE_USERNAME"),
        "password": os.getenv("FAKEWEBSITE_PASSWORD")
    }
])
```

## To Do

- [ ] Add automatic publishing to PyPI
- [ ] Support local S/LLM for email scanning
- [ ] Add support for other password managers

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
