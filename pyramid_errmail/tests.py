import unittest
from pyramid import testing

class Test_errmail_tween_factory(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.registry = self.config.registry

    def handler(self, request): pass

    def _callFUT(self, handler=None, registry=None):
        from pyramid_errmail import errmail_tween_factory
        if handler is None:
            handler = self.handler
        if registry is None:
            registry = self.registry
        return errmail_tween_factory(handler, registry)

    def test_no_recipients(self):
        handler = self._callFUT()
        self.assertEqual(handler, self.handler)

    def test_empty_recipients(self):
        self.registry.settings['errmail.recipients'] = ''
        handler = self._callFUT()
        self.assertEqual(handler, self.handler)

    def test_normal_recipients(self):
        self.registry.settings['errmail.recipients']='chrism@plope.com'
        handler = self._callFUT()
        self.assertNotEqual(handler, self.handler)
        

class Test_errmail_tween(unittest.TestCase):
    def setUp(self):
        from pyramid.request import Request
        request = Request.blank('/')
        self.request = request
        self.config = testing.setUp(request=request)
        self.registry = self.config.registry
        self.registry.settings['errmail.recipients'] = 'chrism'
        request.registry = self.registry

    def _setupMailer(self):
        from pyramid_mailer.testing import includeme
        includeme(self.config)

    def handler(self, request):
        raise NotImplementedError

    def _callFUT(self, handler=None, registry=None, request=None):
        from pyramid_errmail import errmail_tween_factory
        if handler is None:
            handler = self.handler
        if registry is None:
            registry = self.registry
        if request is None:
            request = self.request
        tween = errmail_tween_factory(handler, registry)
        return tween(request)

    def test_nomailer(self):
        from zope.component.registry import ComponentLookupError
        self.assertRaises(ComponentLookupError, self._callFUT)
        

    def test_default(self):
        from pyramid_mailer import get_mailer
        self._setupMailer()
        self.assertRaises(NotImplementedError, self._callFUT)
        mailer = get_mailer(self.request)
        self.assertEqual(len(mailer.outbox), 1)
        message = mailer.outbox[0]
        self.assertEqual(message.sender, 'Pyramid <no-reply@example.com>')
        self.assertEqual(message.recipients, ['chrism'])
        self.assertTrue('Traceback' in message.body)
        self.assertEqual(message.recipients, ['chrism'])
        self.assertTrue(': NotImplementedError() (2' in message.subject)
        self.assertTrue(message.html)
        
    def test_with_sender(self):
        from pyramid_mailer import get_mailer
        self.registry.settings['errmail.sender'] = 'chris'
        self._setupMailer()
        self.assertRaises(NotImplementedError, self._callFUT)
        mailer = get_mailer(self.request)
        self.assertEqual(len(mailer.outbox), 1)
        message = mailer.outbox[0]
        self.assertEqual(message.sender, 'chris')

    def test_with_custom_subject(self):
        from pyramid_mailer import get_mailer
        self.registry.settings['errmail.subject'] = 'foo ${exception}'
        self._setupMailer()
        self.assertRaises(NotImplementedError, self._callFUT)
        mailer = get_mailer(self.request)
        self.assertEqual(len(mailer.outbox), 1)
        message = mailer.outbox[0]
        self.assertEqual(message.subject, 'foo NotImplementedError()')

class Test_includeme(unittest.TestCase):
    def _callFUT(self, config):
        from pyramid_errmail import includeme
        return includeme(config)

    def test_it(self):
        from pyramid_errmail import errmail_tween_factory
        from pyramid.tweens import EXCVIEW
        config = DummyConfig()
        self._callFUT(config)
        self.assertEqual(config.tweens,
                         [(errmail_tween_factory, None, EXCVIEW)])
        self.assertEqual(config.included, ['pyramid_mailer'])

    def test_it_catchall(self):
        from pyramid_errmail import errmail_tween_factory
        from pyramid.tweens import EXCVIEW
        config = DummyConfig()
        config.settings['errmail.catchall'] = 'true'
        self._callFUT(config)
        self.assertEqual(config.tweens,
                         [(errmail_tween_factory, EXCVIEW, None)])
        self.assertEqual(config.included, ['pyramid_mailer'])
        

class DummyConfig(object):
    def __init__(self):
        self.tweens = []
        self.included = []
        self.registry = self
        self.settings = {}

    def add_tween(self, factory, under=None, over=None):
        self.tweens.append((factory, under, over))

    def include(self, path):
        self.included.append(path)
        
