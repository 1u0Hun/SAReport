# -*- coding: utf-8 -*-
from __future__ import with_statement

from flask import current_app as app
from flask.ext.email.backends.locmem import Mail
import flask.ext.email.backends.locmem as mail
from flask.ext.email.message import EmailMessage

from . import BaseEmailBackendTests, FlaskTestCase

class LocmemBackendTests(BaseEmailBackendTests, FlaskTestCase):
    EMAIL_BACKEND = 'flask.ext.email.backends.locmem.Mail'

    def setUp(self):
        super(LocmemBackendTests, self).setUp()
        self.flush_mailbox()

    def get_mailbox_content(self):
        return [m.message() for m in mail.outbox]

    def flush_mailbox(self):
        mail.outbox = []

    def test_locmem_shared_messages(self):
        """
        Make sure that the locmen backend populates the outbox.
        """
        connection = Mail()
        connection2 = Mail()
        email = EmailMessage('Subject', 'Content', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        connection.send_messages([email])
        connection2.send_messages([email])
        self.assertEqual(len(mail.outbox), 2)