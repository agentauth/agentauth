import time

from imap_tools import MailBox

from agentauth import llm

class EmailService:
    def __init__(self, imap_server, imap_port, imap_username, imap_password):
        self.imap_username = imap_username
        self.imap_password = imap_password
        self.imap_server = imap_server
        self.imap_port = imap_port

    def get_code(self, login_start_time) -> str:
        for _ in range(10):
            with MailBox(self.imap_server).login(self.imap_username, self.imap_password) as mailbox:
                for msg in mailbox.fetch(reverse=True):
                    # Ignore emails recieved before this login process started
                    if msg.date < login_start_time:
                        break

                    # Ask LLM if this email contains a login code / for the code
                    query = f"""Does this email contain a login code? If yes, simply respond with the code. If no, simply respond with 'no'.
                    
                    ```
                    {msg.text}
                    ```
                    """
                    response = llm.invoke(query).content
                    if response.lower() == "no":
                        next
                    else:
                        return response
            time.sleep(3)

        return None

    def get_link(self, login_start_time) -> str:
        for _ in range(10):
            with MailBox(self.imap_server).login(self.imap_username, self.imap_password) as mailbox:
                for msg in mailbox.fetch(reverse=True):
                    # Ignore emails recieved before this login process started
                    if msg.date < login_start_time:
                        break

                    # Ask LLM if this email contains a login code / for the code
                    query = f"""Does this email contain a login link? If yes, simply respond with the link. If no, simply respond with 'no'.
                    
                    ```
                    {msg.text}
                    ```
                    """
                    response = llm.invoke(query).content
                    if response.lower() == "no":
                        print("Did not find email link.")
                        next
                    else:
                        print(f"Found email link: {response}")
                        return response
                    
            time.sleep(3)
        
        return None
    