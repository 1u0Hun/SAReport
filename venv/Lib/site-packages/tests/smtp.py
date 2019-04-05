# -*- coding: utf-8 -*-
from __future__ import with_statement

from flask import current_app as app
from flask.ext.email.backends.smtp import Mail

import email
import smtpd
import threading
import asyncore

from . import BaseEmailBackendTests, FlaskTestCase, override_settings

class FakeSMTPServer(smtpd.SMTPServer, threading.Thread):
    """
    Asyncore SMTP server wrapped into a thread. Based on DummyFTPServer from:
    http://svn.python.org/view/python/branches/py3k/Lib/test/test_ftplib.py?revision=86061&view=markup
    """

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        smtpd.SMTPServer.__init__(self, *args, **kwargs)
        self._sink = []
        self.active = False
        self.active_lock = threading.Lock()
        self.sink_lock = threading.Lock()

    def process_message(self, peer, mailfrom, rcpttos, data):
        m = email.message_from_string(data)
        maddr = email.Utils.parseaddr(m.get('from'))[1]
        if mailfrom != maddr:
            return "553 '%s' != '%s'" % (mailfrom, maddr)
        self.sink_lock.acquire()
        self._sink.append(m)
        self.sink_lock.release()

    def get_sink(self):
        self.sink_lock.acquire()
        try:
            return self._sink[:]
        finally:
            self.sink_lock.release()

    def flush_sink(self):
        self.sink_lock.acquire()
        self._sink[:] = []
        self.sink_lock.release()

    def start(self):
        assert not self.active
        self.__flag = threading.Event()
        threading.Thread.start(self)
        self.__flag.wait()

    def run(self):
        self.active = True
        self.__flag.set()
        while self.active and asyncore.socket_map:
            self.active_lock.acquire()
            asyncore.loop(timeout=0.1, count=1)
            self.active_lock.release()
        asyncore.close_all()

    def stop(self):
        assert self.active
        self.active = False
        self.join()


class SMTPBackendTests(BaseEmailBackendTests, FlaskTestCase):
    EMAIL_BACKEND = 'flask.ext.email.backends.smtp.Mail'
    EMAIL_HOST = '127.0.0.1'
    EMAIL_PORT = 2525

    @classmethod
    def setUpClass(cls):
        cls.server = FakeSMTPServer((cls.EMAIL_HOST, cls.EMAIL_PORT), None)
        # cls.settings_override = override_settings(
            # EMAIL_HOST="127.0.0.1",
            # EMAIL_PORT=cls.server.socket.getsockname()[1])
        # cls.settings_override.enable()
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        # cls.settings_override.disable()
        cls.server.stop()

    def setUp(self):
        super(SMTPBackendTests, self).setUp()
        self.server.flush_sink()

    def tearDown(self):
        self.server.flush_sink()
        super(SMTPBackendTests, self).tearDown()

    def flush_mailbox(self):
        self.server.flush_sink()

    def get_mailbox_content(self):
        return self.server.get_sink()

    @override_settings(EMAIL_HOST_USER="not empty username",
                        EMAIL_HOST_PASSWORD="not empty password")
    def test_email_authentication_use_settings(self):
        backend = Mail(app)
        self.assertEqual(backend.username, 'not empty username')
        self.assertEqual(backend.password, 'not empty password')

    @override_settings(EMAIL_HOST_USER="not empty username",
                        EMAIL_HOST_PASSWORD="not empty password")
    def test_email_authentication_override_settings(self):
        backend = Mail(app, username='username', password='password')
        self.assertEqual(backend.username, 'username')
        self.assertEqual(backend.password, 'password')

    @override_settings(EMAIL_HOST_USER="not empty username",
                        EMAIL_HOST_PASSWORD="not empty password")
    def test_email_disabled_authentication(self):
        backend = Mail(app, username='', password='')
        self.assertEqual(backend.username, '')
        self.assertEqual(backend.password, '')