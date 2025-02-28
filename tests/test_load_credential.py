from agentauth import CredentialManager

def main():
    credential_manager = CredentialManager()
    credential_manager.load_credential({
        "website": "https://www.example.com",
        "username": "user@example.com",
        "password": "user_password"
    })

    assert len(credential_manager.credentials) == 1
    assert credential_manager.credentials[0].username == "user@example.com"
    
    credential_manager = CredentialManager()
    credential_manager.load_credentials([
        {
            "website": "https://www.example.com",
            "username": "user1@example.com",
            "password": "user1_password"
        },
        {
            "website": "https://www.example.com", 
            "username": "user2@example.com",
            "password": "user2_password"
        }
    ])

    assert len(credential_manager.credentials) == 2
    assert credential_manager.credentials[0].username == "user1@example.com"

if __name__ == "__main__":
    main()
