from flask.ext.email.backends import rest

from .. import BaseMail


class Mail(BaseMail, rest.Mail):
    pass