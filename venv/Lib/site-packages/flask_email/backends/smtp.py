"""
Send email via SMTP
"""
import smtplib
import socket
import threading

from ..utils import DNS_NAME
from ..message import sanitize_address
from ..signals import email_dispatched
from .base import BaseMail


class Mail(BaseMail):
    """
    A wrapper that manages the SMTP network connection.
    """ 
    def init_app(self, app, host=None, port=None, username=None, password=None,
                 use_tls=None, use_ssl=None, fail_silently=False, **kwargs):
        self.host = host or app.config.get('EMAIL_HOST', 'localhost')
        self.port = int(port or app.config.get('EMAIL_PORT', 25))
        if username is None:
            self.username = app.config.get('EMAIL_HOST_USER')
        else:
            self.username = username
        if password is None:
            self.password = app.config.get('EMAIL_HOST_PASSWORD')
        else:
            self.password = password
        if use_tls is None:
            self.use_tls = bool(app.config.get('EMAIL_USE_TLS', False))
        else:
            self.use_tls = use_tls
        if use_ssl is None:
            self.use_ssl = bool(app.config.get('EMAIL_USE_SSL', False))
        else:
            self.use_ssl = use_ssl
        self.connection = None
        self._lock = threading.RLock()
        super(Mail, self).init_app(app, fail_silently=fail_silently, **kwargs)

    def open(self):
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        try:
            # If local_hostname is not specified, socket.getfqdn() gets used.
            # For performance, we use the cached FQDN for local_hostname.
            SMTP = (smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP)
            self.connection = SMTP(self.host, self.port,
                                           local_hostname=DNS_NAME.get_fqdn())

            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls()
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise

    def close(self):
        """Closes the connection to the email server."""
        try:
            try:
                self.connection.quit()
            except socket.sslerror:
                # This happens when calling quit() on a TLS connection
                # sometimes.
                self.connection.close()
            except:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

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
            if not self.connection:
                # We failed silently on open().
                # Trying to send would be pointless.
                return
            num_sent = 0
            for message in email_messages:
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
        if not email_message.recipients():
            return False
        # if not email_message.from_email:
        #     return False
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, email_message.encoding)
                      for addr in email_message.recipients()]
        try:
            self.connection.sendmail(from_email, recipients,
                    email_message.message().as_string())
        except:
            if not self.fail_silently:
                raise
            return False
        return True