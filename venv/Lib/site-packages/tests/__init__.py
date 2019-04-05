# -*- coding: utf-8 -*-
from __future__ import with_statement

from flask import Flask, current_app as app
import flask.ext.email.backends.locmem as mail
from flask.ext.email.backends.base import BaseMail
from flask.ext.email.backends.console import Mail as ConsoleMail
from flask.ext.email.backends.smtp import Mail as SMTPMail
from flask.ext.email.backends.filebased import Mail as FilebasedMail
from flask.ext.email.backends.locmem import Mail as LocMemMail
from flask.ext.email.backends.dummy import Mail as DummyMail
from flask.ext.email.message import EmailMessage
from flask.ext.email import get_connection, send_mail, send_mass_mail, mail_managers, mail_admins

import unittest
import shutil
import tempfile
from functools import wraps


class override_settings(object):
    """
    Acts as either a decorator, or a context manager. If it's a decorator it
    takes a function and returns a wrapped function. If it's a contextmanager
    it's used with the ``with`` statement. In either event entering/exiting
    are called before and after, respectively, the function/block is executed.
    """
    def __init__(self, **kwargs):
        self.options = kwargs
        self.option_store = None

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def __call__(self, test_func):
        @wraps(test_func)
        def inner(*args, **kwargs):
            with self:
                return test_func(*args, **kwargs)
        return inner

    def enable(self):
        self.option_store = {}
        for key, value in self.options.items():
            self.option_store[key] = app.config.get(key, None)
            app.config[key] = value

    def disable(self):
        for key, value in self.option_store.items():
            app.config[key] = value
        self.option_store = None

class CustomMail(BaseMail):
    def __init__(self, *args, **kwargs):
        super(CustomMail, self).__init__(*args, **kwargs)
        self.test_outbox = []

    def send_messages(self, email_messages):
        # Messages are stored in a instance variable for testing.
        self.test_outbox.extend(email_messages)
        return len(email_messages)


class FlaskTestCase(unittest.TestCase):
    TESTING = True
    DEFAULT_FROM_EMAIL = 'support@mysite.com'

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.from_object(self)
        self.assertTrue(self.app.testing)
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

class GeneralEmailBackendTests(FlaskTestCase):
    def test_dummy_backend(self):
        """
        Make sure that dummy backends returns correct number of sent messages
        """
        connection = DummyMail()
        email = EmailMessage('Subject', 'Content', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        self.assertEqual(connection.send_messages([email, email, email]), 3)

    def test_arbitrary_keyword(self):
        """
        Make sure that get_connection() accepts arbitrary keyword that might be
        used with custom backends.
        """
        c = get_connection(fail_silently=True, foo='bar')
        self.assertTrue(c.fail_silently)

    def test_custom_backend(self):
        """Test custom backend defined in this suite."""
        conn = get_connection('tests.CustomMail')
        self.assertTrue(hasattr(conn, 'test_outbox'))
        email = EmailMessage('Subject', 'Content', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        conn.send_messages([email])
        self.assertEqual(len(conn.test_outbox), 1)

    def test_backend_arg(self):
        """Test backend argument of get_connection()"""
        self.assertTrue(isinstance(get_connection('flask.ext.email.backends.smtp.Mail'), SMTPMail))
        self.assertTrue(isinstance(get_connection('flask.ext.email.backends.locmem.Mail'), LocMemMail))
        self.assertTrue(isinstance(get_connection('flask.ext.email.backends.dummy.Mail'), DummyMail))
        self.assertTrue(isinstance(get_connection('flask.ext.email.backends.console.Mail'), ConsoleMail))
        tmp_dir = tempfile.mkdtemp()
        try:
            self.assertTrue(isinstance(get_connection('flask.ext.email.backends.filebased.Mail', file_path=tmp_dir), FilebasedMail))
        finally:
            shutil.rmtree(tmp_dir)
        self.assertTrue(isinstance(get_connection(), LocMemMail))

    @override_settings(
        EMAIL_BACKEND='flask.ext.email.backends.locmem.Mail',
        ADMINS=[('nobody', 'nobody@example.com')],
        MANAGERS=[('nobody', 'nobody@example.com')])
    def test_connection_arg(self):
        """Test connection argument to send_mail(), et. al."""
        mail.outbox = []

        # Send using non-default connection
        connection = get_connection('tests.CustomMail')
        send_mail('Subject', 'Content', 'from@example.com', ['to@example.com'], connection=connection)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(len(connection.test_outbox), 1)
        self.assertEqual(connection.test_outbox[0].subject, 'Subject')

        connection = get_connection('tests.CustomMail')
        send_mass_mail([
                ('Subject1', 'Content1', 'from1@example.com', ['to1@example.com']),
                ('Subject2', 'Content2', 'from2@example.com', ['to2@example.com']),
            ], connection=connection)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(len(connection.test_outbox), 2)
        self.assertEqual(connection.test_outbox[0].subject, 'Subject1')
        self.assertEqual(connection.test_outbox[1].subject, 'Subject2')

        connection = get_connection('tests.CustomMail')
        mail_admins('Admin message', 'Content', connection=connection)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(len(connection.test_outbox), 1)
        self.assertEqual(connection.test_outbox[0].subject, '[Flask] Admin message')

        connection = get_connection('tests.CustomMail')
        mail_managers('Manager message', 'Content', connection=connection)
        self.assertEqual(mail.outbox, [])
        self.assertEqual(len(connection.test_outbox), 1)
        self.assertEqual(connection.test_outbox[0].subject, '[Flask] Manager message')


class BaseEmailBackendTests(object):
    def assertStartsWith(self, first, second):
        if not first.startswith(second):
            self.longMessage = True
            self.assertEqual(first[:len(second)], second, "First string doesn't start with the second.")

    def get_mailbox_content(self):
        raise NotImplementedError

    def flush_mailbox(self):
        raise NotImplementedError

    def get_the_message(self):
        mailbox = self.get_mailbox_content()
        self.assertEqual(len(mailbox), 1,
            "Expected exactly one message, got %d.\n%r" % (len(mailbox), [
                m.as_string() for m in mailbox]))
        return mailbox[0]

    def test_send(self):
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['to@example.com'])
        num_sent = get_connection().send_messages([email])
        self.assertEqual(num_sent, 1)
        message = self.get_the_message()
        self.assertEqual(message["subject"], "Subject")
        self.assertEqual(message.get_payload(), "Content")
        self.assertEqual(message["from"], "from@example.com")
        self.assertEqual(message.get_all("to"), ["to@example.com"])

    def test_send_many(self):
        email1 = EmailMessage('Subject', 'Content1', 'from@example.com', ['to@example.com'])
        email2 = EmailMessage('Subject', 'Content2', 'from@example.com', ['to@example.com'])
        num_sent = get_connection().send_messages([email1, email2])
        self.assertEqual(num_sent, 2)
        messages = self.get_mailbox_content()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].get_payload(), "Content1")
        self.assertEqual(messages[1].get_payload(), "Content2")

    def test_send_verbose_name(self):
        email = EmailMessage("Subject", "Content", '"Firstname Sürname" <from@example.com>',
                             ["to@example.com"])
        email.send()
        message = self.get_the_message()
        self.assertEqual(message["subject"], "Subject")
        self.assertEqual(message.get_payload(), "Content")
        self.assertEqual(message["from"], "=?utf-8?q?Firstname_S=C3=BCrname?= <from@example.com>")

    @override_settings(MANAGERS=[('nobody', 'nobody@example.com')])
    def test_html_mail_managers(self):
        """Test html_message argument to mail_managers"""
        mail_managers('Subject', 'Content', html_message='HTML Content')
        message = self.get_the_message()

        self.assertEqual(message.get('subject'), '[Flask] Subject')
        self.assertEqual(message.get_all('to'), ['nobody@example.com'])
        self.assertTrue(message.is_multipart())
        self.assertEqual(len(message.get_payload()), 2)
        self.assertEqual(message.get_payload(0).get_payload(), 'Content')
        self.assertEqual(message.get_payload(0).get_content_type(), 'text/plain')
        self.assertEqual(message.get_payload(1).get_payload(), 'HTML Content')
        self.assertEqual(message.get_payload(1).get_content_type(), 'text/html')

    @override_settings(ADMINS=[('nobody', 'nobody@example.com')])
    def test_html_mail_admins(self):
        """Test html_message argument to mail_admins """
        mail_admins('Subject', 'Content', html_message='HTML Content')
        message = self.get_the_message()

        self.assertEqual(message.get('subject'), '[Flask] Subject')
        self.assertEqual(message.get_all('to'), ['nobody@example.com'])
        self.assertTrue(message.is_multipart())
        self.assertEqual(len(message.get_payload()), 2)
        self.assertEqual(message.get_payload(0).get_payload(), 'Content')
        self.assertEqual(message.get_payload(0).get_content_type(), 'text/plain')
        self.assertEqual(message.get_payload(1).get_payload(), 'HTML Content')
        self.assertEqual(message.get_payload(1).get_content_type(), 'text/html')

    @override_settings(
        ADMINS=[('nobody', 'nobody+admin@example.com')],
        MANAGERS=[('nobody', 'nobody+manager@example.com')])
    def test_manager_and_admin_mail_prefix(self):
        """
        String prefix + lazy translated subject = bad output
        Regression for #13494
        """
        mail_managers('Subject', 'Content')
        message = self.get_the_message()
        self.assertEqual(message.get('subject'), '[Flask] Subject')

        self.flush_mailbox()
        mail_admins('Subject', 'Content')
        message = self.get_the_message()
        self.assertEqual(message.get('subject'), '[Flask] Subject')

    @override_settings(ADMINS=(), MANAGERS=())
    def test_empty_admins(self):
        """
        Test that mail_admins/mail_managers doesn't connect to the mail server
        if there are no recipients (#9383)
        """
        mail_admins('hi', 'there')
        self.assertEqual(self.get_mailbox_content(), [])
        mail_managers('hi', 'there')
        self.assertEqual(self.get_mailbox_content(), [])

    def test_message_cc_header(self):
        """
        Regression test for Django #7722
        """
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['to@example.com'], cc=['cc@example.com'])
        get_connection().send_messages([email])
        message = self.get_the_message()
        self.assertStartsWith(message.as_string(), 'Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: Subject\nFrom: from@example.com\nTo: to@example.com\nCc: cc@example.com\nDate: ')

    def test_idn_send(self):
        """
        Regression test for Django #14301
        """
        self.assertTrue(send_mail('Subject', 'Content', 'from@öäü.com', [u'to@öäü.com']))
        message = self.get_the_message()
        self.assertEqual(message.get('subject'), 'Subject')
        self.assertEqual(message.get('from'), 'from@xn--4ca9at.com')
        self.assertEqual(message.get('to'), 'to@xn--4ca9at.com')

        self.flush_mailbox()
        m = EmailMessage('Subject', 'Content', 'from@öäü.com',
                     [u'to@öäü.com'], cc=[u'cc@öäü.com'])
        m.send()
        message = self.get_the_message()
        self.assertEqual(message.get('subject'), 'Subject')
        self.assertEqual(message.get('from'), 'from@xn--4ca9at.com')
        self.assertEqual(message.get('to'), 'to@xn--4ca9at.com')
        self.assertEqual(message.get('cc'), 'cc@xn--4ca9at.com')

    def test_recipient_without_domain(self):
        """
        Regression test for Django #15042
        """
        self.assertTrue(send_mail("Subject", "Content", "tester", ["django"]))
        message = self.get_the_message()
        self.assertEqual(message.get('subject'), 'Subject')
        self.assertEqual(message.get('from'), "tester")
        self.assertEqual(message.get('to'), "django")

if __name__ == '__main__':
    unittest.main()