# -*- coding: utf-8 -*-
"""
    flask.ext.email
    ~~~~~~~~~~~~~~~

    Flask extension for sending email.

"""
__version__ = '1.4.3'

"""
Tools for sending email.
"""

from flask import current_app as app
from .utils import import_module

# Imported for backwards compatibility, and for the sake
# of a cleaner namespace. These symbols used to be in
# django/core/mail.py before the introduction of email
# backends and the subsequent reorganization (See #10355)
from .utils import CachedDnsName, DNS_NAME
from .message import (
    EmailMessage, EmailMultiAlternatives,
    SafeMIMEText, SafeMIMEMultipart,
    DEFAULT_ATTACHMENT_MIME_TYPE, make_msgid,
    BadHeaderError, forbid_multi_line_headers)
from .backends.console import Mail as ConsoleMail
from .backends.dummy import Mail as DummyMail
from .backends.filebased import Mail as FilebasedMail
from .backends.locmem import Mail as LocmemMail
from .backends.smtp import Mail as SMTPMail
from .backends.rest import Mail as RESTMail


def get_connection(backend=None, fail_silently=False, **kwargs):
    """
    Load an email backend and return an instance of it.

    If backend is None (default) EMAIL_BACKEND is used.

    Both fail_silently and other keyword arguments are used in the
    constructor of the backend.
    """
    path = backend or app.config.get('EMAIL_BACKEND', 'flask.ext.email.backends.locmem.Mail')
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise Exception(('Error importing email backend module %s: "%s"'
                                    % (mod_name, e)))
    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise Exception(('Module "%s" does not define a '
                                    '"%s" class' % (mod_name, klass_name)))
    return klass(app, fail_silently=fail_silently, **kwargs)


def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(username=auth_user,
                                    password=auth_password,
                                    fail_silently=fail_silently)
    return EmailMessage(subject, message, from_email, recipient_list,
                        connection=connection).send()


def send_mass_mail(datatuple, fail_silently=False, auth_user=None,
                   auth_password=None, connection=None):
    """
    Given a datatuple of (subject, message, from_email, recipient_list), sends
    each message to each recipient list. Returns the number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    connection = connection or get_connection(username=auth_user,
                                    password=auth_password,
                                    fail_silently=fail_silently)
    messages = [EmailMessage(subject, message, sender, recipient)
                for subject, message, sender, recipient in datatuple]
    return connection.send_messages(messages)


def mail_admins(subject, message, fail_silently=False, connection=None,
                html_message=None):
    """Sends a message to the admins, as defined by the ADMINS setting."""
    if not app.config.get('ADMINS', None):
        return
    mail = EmailMultiAlternatives(u'%s%s' % (app.config.get('EMAIL_SUBJECT_PREFIX', '[Flask] '), subject),
                message, app.config.get('SERVER_EMAIL', 'root@localhost'), [a[1] for a in app.config['ADMINS']],
                connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')
    mail.send(fail_silently=fail_silently)


def mail_managers(subject, message, fail_silently=False, connection=None,
                  html_message=None):
    """Sends a message to the managers, as defined by the MANAGERS setting."""
    if not app.config.get('MANAGERS', None):
        return
    mail = EmailMultiAlternatives(u'%s%s' % (app.config.get('EMAIL_SUBJECT_PREFIX', '[Flask] '), subject),
                message, app.config.get('SERVER_EMAIL', 'root@localhost'), [a[1] for a in app.config['MANAGERS']],
                connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')
    mail.send(fail_silently=fail_silently)