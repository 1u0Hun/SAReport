# -*- coding: utf-8 -*-
from __future__ import with_statement

from flask.ext.email import get_connection, send_mail

from email import message_from_string
import sys
from StringIO import StringIO
from functools import wraps

from . import BaseEmailBackendTests, FlaskTestCase

class ConsoleBackendTests(BaseEmailBackendTests, FlaskTestCase):
    EMAIL_BACKEND = 'flask.ext.email.backends.console.Mail'

    def setUp(self):
        super(ConsoleBackendTests, self).setUp()
        self.__stdout = sys.stdout
        self.stream = sys.stdout = StringIO()

    def tearDown(self):
        del self.stream
        sys.stdout = self.__stdout
        del self.__stdout
        super(ConsoleBackendTests, self).tearDown()

    def flush_mailbox(self):
        self.stream = sys.stdout = StringIO()

    def get_mailbox_content(self):
        messages = self.stream.getvalue().split('\n' + ('-' * 79) + '\n')
        return [message_from_string(m) for m in messages if m]

    def test_console_stream_kwarg(self):
        """
        Test that the console backend can be pointed at an arbitrary stream.
        """
        s = StringIO()
        connection = get_connection(self.EMAIL_BACKEND, stream=s)
        send_mail('Subject', 'Content', 'from@example.com', ['to@example.com'], connection=connection)
        self.assertTrue(s.getvalue().startswith('Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Subject\nFrom: from@example.com\nTo: to@example.com\nDate: '))
