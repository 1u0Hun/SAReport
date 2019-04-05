from .base import BaseMail

class Mail(BaseMail):
    """
    Dummy email backend that does nothing.
    """
    def send_messages(self, email_messages):
        return len(email_messages)
