"""Base email backend class."""

class BaseMail(object):
    """
    Base class for email backend implementations.

    Subclasses must at least overwrite :meth:`send_messages`.
    """
    # TODO: Add threadsafe warning
    
    def __init__(self, app=None, **kwargs):
        if app is not None: 
            self.init_app(app, **kwargs)

    def init_app(self, app, fail_silently=False, **kwargs):
        """
        Initializes your mail settings from the application
        settings.

        You can use this if you want to set up your Mail instance
        at configuration time.

        :param app: Flask application instance
        :param bool fail_silently: Email fails silently on errors
        """
        self.fail_silently = fail_silently

        self.app = app


    def open(self):
        """Open a network connection.

        This method can be overwritten by backend implementations to
        open a network connection.

        It's up to the backend implementation to track the status of
        a network connection if it's needed by the backend.

        This method can be called by applications to force a single
        network connection to be used when sending mails. See the
        :meth:`send_messages` method of the SMTP backend for a reference
        implementation.

        The default implementation does nothing.
        """
        pass

    def close(self):
        """Close a network connection."""
        pass

    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.

        Not Implemented
        """
        raise NotImplementedError