# AgentAuth

AgentAuth is a Python package that helps automate web authentication by simulating human-like login behavior. It supports various authentication methods including:
- Standard username/password login
- Time-based One-Time Passwords (TOTP)
- Email magic links
- Email verification codes
- Dynamic and multiple-step login flows

## Features

- 🤖 **Automated Authentication**: Handles complex login flows automatically
- 📧 **Email Integration**: Supports email-based verification (magic links and codes)
- 🔐 **Password Manager Integration**: Works with 1Password, Bitwarden, and local credential storage
- 🌐 **Remote Browser Integration**: Compatible with remote CDP-based browsers to avoid bot detection

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
    "password": os.getenv("PASSWORD"),
    "totp_secret": os.getenv("TOTP_SECRET")  # Optional
})

# Load a list of credentials
credential_manager.load_credentials([
    {
        "website": "https://www.example.com",
        "username": os.getenv("EXAMPLE_USERNAME"),
        "password": os.getenv("EXAMPLE_PASSWORD"),
        "totp_secret": os.getenv("EXAMPLE_TOTP_SECRET")  # Optional
    },
    {
        "website": "https://www.fakewebsite.com",
        "username": os.getenv("FAKEWEBSITE_USERNAME"),
        "password": os.getenv("FAKEWEBSITE_PASSWORD")
    }
])
```

## Connecting to a remote browser

Remote browser services like [Anchor Browser](https://anchorbrowser.io) and [Browserbase](https://browserbase.com) are very helpful to avoid bot detection during authentication. AgentAuth supports remote browsers by accepting a `cdp_url`. See more in the examples directory.

```python
aa = AgentAuth(
    # Add credential manager and/or email config
)

# Automaticaly authenticate using a remote browser session
cdp_url = get_remote_browser_session()
cookies = await aa.auth(
    "https://www.example.com",
    "user@example.com",
    cdp_url=cdp_url
)
```

## Accessing credentials directly

You can access credential values directly from the `CredentialManager` class when you want to handle the authentication process manually. This is useful when you need more control over the login flow or when automatic authentication isn't suitable for your use case.

```python
from agentauth import CredentialManager

credential_manager = CredentialManager()
credential_manager.load_file("credentials.json")

# Get a credential for a specific website and username
credential = credential_manager.get_credential("https://www.example.com", "user@example.com")

# Pull out credential values to use in a login flow
username = credential.username
password = credential.password
totp_code = credential.totp()  # If there is a TOTP secret, this returns the current code
```

## To Do

- [ ] Add automatic publishing to PyPI
- [ ] Support local S/LLM for email scanning
- [ ] Add support for other password managers

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
