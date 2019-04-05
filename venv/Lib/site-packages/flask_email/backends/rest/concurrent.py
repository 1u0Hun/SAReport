"""
Asynchronous REST email backend class via grequests.
"""
import warnings
import requests
import grequests
warnings.warn('grequests has a problem running with Flask with the following \
    error gevent is only usable from a single thread', RuntimeWarning)

from . import Mail as RESTMail


class Mail(RESTMail):
    def init_app(self, app, concurrency=None, **kwargs):
        self.concurrency = concurrency
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

            reqs = [grequests.post(self.endpoint, 
                **self._prepare_request_kwargs(msg)
            ) for msg in email_messages if msg.recipients()]

            responses = grequests.map(reqs, size=self.concurrency)

            for response in responses:
                if response.status_code != requests.codes.ok:
                    if not self.fail_silently:
                        raise Exception(response.text)
                else:
                    num_sent += 1
            if new_conn_created:
                self.close()
        finally:
            self._lock.release()
        return num_sent