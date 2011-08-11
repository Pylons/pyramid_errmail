import cgitb
import sys
import time
import traceback
import platform
import re
from functools import partial

from pyramid.tweens import EXCVIEW
from pyramid.settings import asbool

from pyramid_mailer.message import Message
from pyramid_mailer import get_mailer

NAME_RE = r"[a-zA-Z][-a-zA-Z0-9_]*"

_interp_regex = re.compile(r'(?<!\$)(\$(?:(%(n)s)|{(%(n)s)}))'
    % ({'n': NAME_RE}))

def errmail_tween_factory(handler, registry):

    sender = registry.settings.get('pyramid_errmail.sender',
                                   'Pyramid <no-reply@example.com>')
    recipients = registry.settings.get('pyramid_errmail.recipients', '')
    subject = registry.settings.get('pyramid_errmail.subject',
                                    '${hostname}: ${exception} (${localtime})')

    recipients = [ x.strip() for x in recipients.splitlines() ]

    if not recipients:
        return handler

    hostname = platform.node()

    def errmail_tween(request, subject=subject):
        try:
            return handler(request)
        except Exception, e:
            try:
                exc_info = sys.exc_info()
                mailer = get_mailer(request)
                exc_repr = repr(e)[:200]
                localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                gmtime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                mapping = {'localtime':localtime,
                           'gmtime':gmtime,
                           'hostname':hostname,
                           'exception':exc_repr}
                def replace(match):
                    whole, param1, param2 = match.groups()
                    return mapping.get(param1 or param2, whole)
                subject = _interp_regex.sub(replace, subject)
                html = cgitb.html(exc_info)
                header = request.url
                html = '<html><h1>%s</h1>%s</html>' % (header, html)
                body = ''.join(traceback.format_exception(*exc_info))
                body = '%s\n\n%s' % (header, body)
                message = Message(subject=subject,
                                  sender=sender,
                                  recipients=recipients,
                                  html=html,
                                  body=body)
                mailer.send_immediately(message, fail_silently=True)
                raise
            finally:
                del exc_info

    return errmail_tween

def includeme(config):
    """
    Set up am implicit 'tween' to send emails when an exception is raised by
    your Pyramid application.

    By default this tween configured to be place 'above' the exception view
    tween, which will cause only exceptions which are not caught by an
    exception view to be mailed.

    The tween can alternately be configured to be placed between the main
    Pyramid app and the Pyramid exception view tween, which will cause *all*
    exceptions (even those eventually caught by a Pyramid exception view,
    which will include exceptions such as ``HTTPFound`` and others
    signifiying redirects) to be mailed.  To turn this feature on, use the
    ``pyramid_errmail.catchall`` configuration setting with a value of
    ``true``.
    """
    config.include('pyramid_mailer')
    catchall = config.registry.settings.get('pyramid_errmail.catchall','false')
    catchall = asbool(catchall)
    add = partial(config.add_tween, errmail_tween_factory, alias='errmail')
    if catchall:
        add(under=EXCVIEW)
    else:
        add(over=EXCVIEW)
