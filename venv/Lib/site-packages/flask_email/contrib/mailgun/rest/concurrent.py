from flask.ext.email.backends.rest import concurrent

class Mail(BaseMail, concurrent.Mail):
    pass