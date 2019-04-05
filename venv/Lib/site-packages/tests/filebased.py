# -*- coding: utf-8 -*-
from __future__ import with_statement

from flask.ext.email.message import EmailMessage
from flask.ext.email import get_connection

from email import message_from_string, message_from_file
import os
import shutil
import tempfile

from . import BaseEmailBackendTests, FlaskTestCase, override_settings

class FileBackendTests(BaseEmailBackendTests, FlaskTestCase):
    EMAIL_BACKEND = 'flask.ext.email.backends.filebased.Mail'

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp_dir)
        # self.settings_override = override_settings(EMAIL_FILE_PATH=self.tmp_dir)
        # self.settings_override.enable()
        self.EMAIL_FILE_PATH = self.tmp_dir
        super(FileBackendTests, self).setUp()

    def tearDown(self):
        # self.settings_override.disable()
        super(FileBackendTests, self).tearDown()

    def flush_mailbox(self):
        for filename in os.listdir(self.tmp_dir):
            os.unlink(os.path.join(self.tmp_dir, filename))

    def get_mailbox_content(self):
        messages = []
        for filename in os.listdir(self.tmp_dir):
            session = open(os.path.join(self.tmp_dir, filename)).read().split('\n' + ('-' * 79) + '\n')
            messages.extend(message_from_string(m) for m in session if m)
        return messages

    def test_file_sessions(self):
        """Make sure opening a connection creates a new file"""
        msg = EmailMessage('Subject', 'Content', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        connection = get_connection()
        connection.send_messages([msg])

        self.assertEqual(len(os.listdir(self.tmp_dir)), 1)
        message = message_from_file(open(os.path.join(self.tmp_dir, os.listdir(self.tmp_dir)[0])))
        self.assertEqual(message.get_content_type(), 'text/plain')
        self.assertEqual(message.get('subject'), 'Subject')
        self.assertEqual(message.get('from'), 'from@example.com')
        self.assertEqual(message.get('to'), 'to@example.com')

        connection2 = get_connection()
        connection2.send_messages([msg])
        self.assertEqual(len(os.listdir(self.tmp_dir)), 2)

        connection.send_messages([msg])
        self.assertEqual(len(os.listdir(self.tmp_dir)), 2)

        msg.connection = get_connection()
        self.assertTrue(connection.open())
        msg.send()
        self.assertEqual(len(os.listdir(self.tmp_dir)), 3)
        msg.send()
        self.assertEqual(len(os.listdir(self.tmp_dir)), 3)