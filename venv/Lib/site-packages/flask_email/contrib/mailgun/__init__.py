from flask.ext.email.backends import rest


class BaseMail(object):
    def init_app(self, app, api_key=None, mailgun_domain=None, **kwargs):
        if api_key is None:
            raise Exception('API Key required for Mailgun')
        else:
            self.api_key = api_key
        kwargs['endpoint'] = 'https://api.mailgun.net/v2/{domain}/messages'.format(domain=mailgun_domain)
        super(BaseMail, self).init_app(app, **kwargs)

    def _prepare_request_kwargs(self, email_message):
        kwargs = super(BaseMail, self)._prepare_request_kwargs(email_message)
        kwargs.update({
            'auth': ('api', self.api_key),
        })

        # Find alternatives, only takes 1 HTML alternative
        if hasattr(email_message, 'alternatives'):
            for content, mimetype in email_message.alternatives:
                if mimetype in ['text/html']:
                    kwargs.setdefault('data', {})
                    kwargs['data']['html'] = content
                    break
        return kwargs