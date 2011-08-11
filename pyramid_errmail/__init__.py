import sys
import traceback
from functools import partial

from pyramid.tweens import EXCVIEW
from pyramid.settings import asbool

from pyramid_mailer.message import Message
from pyramid_mailer import get_mailer

def errmail_tween_factory(handler, registry):

    sender = registry.settings.get('pyramid_errmail.sender',
                                   'Pyramid <no-reply@example.com>')
    recipients = registry.settings.get('pyramid_errmail.recipients')
    subject = registry.settings.get('pyramid_errmail.subject')

    if recipients is None:
        return handler

    recipients = [ x.strip() for x in recipients.splitlines() ]

    if not recipients:
        return handler

    def errmail_tween(request, subject=subject):
        try:
            return handler(request)
        except Exception, e:
            mailer = get_mailer(request)
            if subject is None:
                subject = repr(e)
            body = ''.join(traceback.format_exception(*sys.exc_info()))
            message = Message(subject=subject,
                              sender=sender,
                              recipients=recipients,
                              body=body)
            mailer.send_immediately(message, fail_silently=True)
            raise

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
