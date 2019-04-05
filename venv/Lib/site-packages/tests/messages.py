# -*- coding: utf-8 -*-
from __future__ import with_statement

from flask.ext.email.message import EmailMessage, EmailMultiAlternatives
from flask.ext.email.message import BadHeaderError

from email import message_from_string

from . import FlaskTestCase, override_settings


class MessageTests(FlaskTestCase):
    """
    Non-backend specific tests.
    """

    def test_ascii(self):
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['to@example.com'])
        message = email.message()
        self.assertEqual(message['Subject'].encode(), 'Subject')
        self.assertEqual(message.get_payload(), 'Content')
        self.assertEqual(message['From'], 'from@example.com')
        self.assertEqual(message['To'], 'to@example.com')

    def test_multiple_recipients(self):
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['to@example.com', 'other@example.com'])
        message = email.message()
        self.assertEqual(message['Subject'].encode(), 'Subject')
        self.assertEqual(message.get_payload(), 'Content')
        self.assertEqual(message['From'], 'from@example.com')
        self.assertEqual(message['To'], 'to@example.com, other@example.com')

    def test_cc(self):
        """Regression test for Django #7722"""
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['to@example.com'], cc=['cc@example.com'])
        message = email.message()
        self.assertEqual(message['Cc'], 'cc@example.com')
        self.assertEqual(email.recipients(), ['to@example.com', 'cc@example.com'])

        # Test multiple CC with multiple To
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['to@example.com', 'other@example.com'], cc=['cc@example.com', 'cc.other@example.com'])
        message = email.message()
        self.assertEqual(message['Cc'], 'cc@example.com, cc.other@example.com')
        self.assertEqual(email.recipients(), ['to@example.com', 'other@example.com', 'cc@example.com', 'cc.other@example.com'])

        # Testing with Bcc
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['to@example.com', 'other@example.com'], cc=['cc@example.com', 'cc.other@example.com'], bcc=['bcc@example.com'])
        message = email.message()
        self.assertEqual(message['Cc'], 'cc@example.com, cc.other@example.com')
        self.assertEqual(email.recipients(), ['to@example.com', 'other@example.com', 'cc@example.com', 'cc.other@example.com', 'bcc@example.com'])

    def test_recipients_as_tuple(self):
        email = EmailMessage('Subject', 'Content', 'from@example.com', ('to@example.com', 'other@example.com'), cc=('cc@example.com', 'cc.other@example.com'), bcc=('bcc@example.com',))
        message = email.message()
        self.assertEqual(message['Cc'], 'cc@example.com, cc.other@example.com')
        self.assertEqual(email.recipients(), ['to@example.com', 'other@example.com', 'cc@example.com', 'cc.other@example.com', 'bcc@example.com'])

    def test_header_injection(self):
        email = EmailMessage('Subject\nInjection Test', 'Content', 'from@example.com', ['to@example.com'])
        self.assertRaises(BadHeaderError, email.message)
        # email = EmailMessage(ugettext_lazy('Subject\nInjection Test'), 'Content', 'from@example.com', ['to@example.com'])
        # self.assertRaises(BadHeaderError, email.message)

    def test_space_continuation(self):
        """
        Test for space continuation character in long (ascii) subject headers (#7747)
        """
        email = EmailMessage('Long subject lines that get wrapped should use a space continuation character to get expected behavior in Outlook and Thunderbird', 'Content', 'from@example.com', ['to@example.com'])
        message = email.message()
        self.assertEqual(message['Subject'], 'Long subject lines that get wrapped should use a space continuation\n character to get expected behavior in Outlook and Thunderbird')

    def test_message_header_overrides(self):
        """
        Specifying dates or message-ids in the extra headers overrides the
        default values (#9233)
        """
        headers = {"date": "Fri, 09 Nov 2001 01:08:47 -0000", "Message-ID": "foo"}
        email = EmailMessage('subject', 'content', 'from@example.com', ['to@example.com'], headers=headers)
        self.assertEqual(email.message().as_string(), 'Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: subject\nFrom: from@example.com\nTo: to@example.com\ndate: Fri, 09 Nov 2001 01:08:47 -0000\nMessage-ID: foo\n\ncontent')

    def test_from_header(self):
        """
        Make sure we can manually set the From header (#9214)
        """
        email = EmailMessage('Subject', 'Content', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        message = email.message()
        self.assertEqual(message['From'], 'from@example.com')

    def test_to_header(self):
        """
        Make sure we can manually set the To header (#17444)
        """
        email = EmailMessage('Subject', 'Content', 'bounce@example.com',
                             ['list-subscriber@example.com', 'list-subscriber2@example.com'],
                             headers={'To': 'mailing-list@example.com'})
        message = email.message()
        self.assertEqual(message['To'], 'mailing-list@example.com')
        self.assertEqual(email.to, ['list-subscriber@example.com', 'list-subscriber2@example.com'])

        # If we don't set the To header manually, it should default to the `to` argument to the constructor
        email = EmailMessage('Subject', 'Content', 'bounce@example.com',
                             ['list-subscriber@example.com', 'list-subscriber2@example.com'])
        message = email.message()
        self.assertEqual(message['To'], 'list-subscriber@example.com, list-subscriber2@example.com')
        self.assertEqual(email.to, ['list-subscriber@example.com', 'list-subscriber2@example.com'])

    def test_multiple_message_call(self):
        """
        Regression for #13259 - Make sure that headers are not changed when
        calling EmailMessage.message()
        """
        email = EmailMessage('Subject', 'Content', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        message = email.message()
        self.assertEqual(message['From'], 'from@example.com')
        message = email.message()
        self.assertEqual(message['From'], 'from@example.com')

    def test_unicode_address_header(self):
        """
        Regression for #11144 - When a to/from/cc header contains unicode,
        make sure the email addresses are parsed correctly (especially with
        regards to commas)
        """
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['"Firstname Sürname" <to@example.com>', 'other@example.com'])
        self.assertEqual(email.message()['To'], '=?utf-8?q?Firstname_S=C3=BCrname?= <to@example.com>, other@example.com')
        email = EmailMessage('Subject', 'Content', 'from@example.com', ['"Sürname, Firstname" <to@example.com>', 'other@example.com'])
        self.assertEqual(email.message()['To'], '=?utf-8?q?S=C3=BCrname=2C_Firstname?= <to@example.com>, other@example.com')

    def test_unicode_headers(self):
        email = EmailMessage(u"Gżegżółka", "Content", "from@example.com", ["to@example.com"],
                             headers={"Sender": '"Firstname Sürname" <sender@example.com>',
                                      "Comments": 'My Sürname is non-ASCII'})
        message = email.message()
        self.assertEqual(message['Subject'], '=?utf-8?b?R8W8ZWfFvMOzxYJrYQ==?=')
        self.assertEqual(message['Sender'], '=?utf-8?q?Firstname_S=C3=BCrname?= <sender@example.com>')
        self.assertEqual(message['Comments'], '=?utf-8?q?My_S=C3=BCrname_is_non-ASCII?=')

    def test_safe_mime_multipart(self):
        """
        Make sure headers can be set with a different encoding than utf-8 in
        SafeMIMEMultipart as well
        """
        headers = {"Date": "Fri, 09 Nov 2001 01:08:47 -0000", "Message-ID": "foo"}
        subject, from_email, to = 'hello', 'from@example.com', '"Sürname, Firstname" <to@example.com>'
        text_content = 'This is an important message.'
        html_content = '<p>This is an <strong>important</strong> message.</p>'
        msg = EmailMultiAlternatives('Message from Firstname Sürname', text_content, from_email, [to], headers=headers)
        msg.attach_alternative(html_content, "text/html")
        msg.encoding = 'iso-8859-1'
        self.assertEqual(msg.message()['To'], '=?iso-8859-1?q?S=FCrname=2C_Firstname?= <to@example.com>')
        self.assertEqual(msg.message()['Subject'].encode(), u'=?iso-8859-1?q?Message_from_Firstname_S=FCrname?=')

    def test_encoding(self):
        """
        Regression for #12791 - Encode body correctly with other encodings
        than utf-8
        """
        email = EmailMessage('Subject', 'Firstname Sürname is a great guy.', 'from@example.com', ['other@example.com'])
        email.encoding = 'iso-8859-1'
        message = email.message()
        self.assertTrue(message.as_string().startswith('Content-Type: text/plain; charset="iso-8859-1"\nMIME-Version: 1.0\nContent-Transfer-Encoding: quoted-printable\nSubject: Subject\nFrom: from@example.com\nTo: other@example.com'))
        self.assertEqual(message.get_payload(), 'Firstname S=FCrname is a great guy.')

        # Make sure MIME attachments also works correctly with other encodings than utf-8
        text_content = 'Firstname Sürname is a great guy.'
        html_content = '<p>Firstname Sürname is a <strong>great</strong> guy.</p>'
        msg = EmailMultiAlternatives('Subject', text_content, 'from@example.com', ['to@example.com'])
        msg.encoding = 'iso-8859-1'
        msg.attach_alternative(html_content, "text/html")
        self.assertEqual(msg.message().get_payload(0).as_string(), 'Content-Type: text/plain; charset="iso-8859-1"\nMIME-Version: 1.0\nContent-Transfer-Encoding: quoted-printable\n\nFirstname S=FCrname is a great guy.')
        self.assertEqual(msg.message().get_payload(1).as_string(), 'Content-Type: text/html; charset="iso-8859-1"\nMIME-Version: 1.0\nContent-Transfer-Encoding: quoted-printable\n\n<p>Firstname S=FCrname is a <strong>great</strong> guy.</p>')

    def test_attachments(self):
        """Regression test for Django #9367"""
        headers = {"Date": "Fri, 09 Nov 2001 01:08:47 -0000", "Message-ID": "foo"}
        subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
        text_content = 'This is an important message.'
        html_content = '<p>This is an <strong>important</strong> message.</p>'
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to], headers=headers)
        msg.attach_alternative(html_content, "text/html")
        msg.attach("an attachment.pdf", "%PDF-1.4.%...", mimetype="application/pdf")
        msg_str = msg.message().as_string()
        message = message_from_string(msg_str)
        self.assertTrue(message.is_multipart())
        self.assertEqual(message.get_content_type(), 'multipart/mixed')
        self.assertEqual(message.get_default_type(), 'text/plain')
        payload = message.get_payload()
        self.assertEqual(payload[0].get_content_type(), 'multipart/alternative')
        self.assertEqual(payload[1].get_content_type(), 'application/pdf')

    def test_non_ascii_attachment_filename(self):
        """Regression test for Django #14964"""
        headers = {"Date": "Fri, 09 Nov 2001 01:08:47 -0000", "Message-ID": "foo"}
        subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
        content = 'This is the message.'
        msg = EmailMessage(subject, content, from_email, [to], headers=headers)
        # Unicode in file name
        msg.attach(u"une pièce jointe.pdf", "%PDF-1.4.%...", mimetype="application/pdf")
        msg_str = msg.message().as_string()
        message = message_from_string(msg_str)
        payload = message.get_payload()
        self.assertEqual(payload[1].get_filename(), u'une pièce jointe.pdf')

    def test_dont_mangle_from_in_body(self):
        # Regression for #13433 - Make sure that EmailMessage doesn't mangle
        # 'From ' in message body.
        email = EmailMessage('Subject', 'From the future', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        self.assertFalse('>From the future' in email.message().as_string())

    def test_dont_base64_encode(self):
        # Ticket #3472
        # Shouldn't use Base64 encoding at all
        msg = EmailMessage('Subject', 'UTF-8 encoded body', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        self.assertFalse('Content-Transfer-Encoding: base64' in msg.message().as_string())

        # Ticket #11212
        # Shouldn't use quoted printable, should detect it can represent content with 7 bit data
        msg = EmailMessage('Subject', 'Body with only ASCII characters.', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        s = msg.message().as_string()
        self.assertFalse('Content-Transfer-Encoding: quoted-printable' in s)
        self.assertTrue('Content-Transfer-Encoding: 7bit' in s)

        # Shouldn't use quoted printable, should detect it can represent content with 8 bit data
        msg = EmailMessage('Subject', 'Body with latin characters: àáä.', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        s = msg.message().as_string()
        self.assertFalse('Content-Transfer-Encoding: quoted-printable' in s)
        self.assertTrue('Content-Transfer-Encoding: 8bit' in s)

        msg = EmailMessage('Subject', u'Body with non latin characters: А Б В Г Д Е Ж Ѕ З И І К Л М Н О П.', 'bounce@example.com', ['to@example.com'], headers={'From': 'from@example.com'})
        s = msg.message().as_string()
        self.assertFalse('Content-Transfer-Encoding: quoted-printable' in s)
        self.assertTrue('Content-Transfer-Encoding: 8bit' in s)