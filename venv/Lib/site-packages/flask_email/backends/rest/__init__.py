"""
REST email backend class via requests.
"""
from flask.ext.email.backends.base import BaseMail
from flask.ext.email.message import sanitize_address

import threading
import requests


class Mail(BaseMail):
    def init_app(self, app, endpoint=None, **kwargs):
        if endpoint is None:
            raise Exception('API endpoint required')
        else:
            self.endpoint = endpoint

        self._lock = threading.RLock()
        super(Mail, self).init_app(app, **kwargs)

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return
        self._lock.acquire()
        try:
            new_conn_created = self.open()
            num_sent = 0
            for message in email_messages:
                if not message.recipients():
                    continue
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
        finally:
            self._lock.release()
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        try:
            response = requests.post(self.endpoint, 
                **self._prepare_request_kwargs(email_message)
            )
            if response.status_code != requests.codes.ok:
                if not self.fail_silently:
                    raise Exception(response.text)
                return False
            return True
        except:
            if not self.fail_silently:
                raise
        return False

    def _prepare_request_kwargs(self, email_message):
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
              for addr in email_message.recipients()]

        return {
            'data': {
                'from': from_email,
                'to': recipients,
                'subject': email_message.subject,
                'text': email_message.body,
            }
        }