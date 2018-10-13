from unittest import TestCase
import time

from webtest import TestApp

from pyramid.security import (Everyone, Authenticated, Allow, Deny,
                              NO_PERMISSION_REQUIRED,
                              )
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from zope.interface import implementer

from gandi_pyramid_prometheus import prometheus as prom
from prometheus_client import REGISTRY
from prometheus_client.parser import text_string_to_metric_families


class Context(object):
    __acl__ = [
        (Allow, Everyone, NO_PERMISSION_REQUIRED),
        (Allow, 'metrics', ['prometheus:metric:read']),
        (Allow, 'user', ['authenticated']),
        ]

    def __init__(self, request):
        pass


@implementer(IAuthenticationPolicy)
class AuthenticationPolicy(object):

    def authenticated_userid(self, request):
        authorization = request.headers.get('Authorization')
        if authorization == 'Bearer prometheus':
            return 'prometheus'
        return 'user'

    def effective_principals(self, request):
        account = self.authenticated_userid(request)
        if account == 'prometheus':
            return ['metrics']
        elif account == 'user':
            return ['authenticated']
        return []

    def unauthenticated_userid(self, request):
        return request.headers.get('Authorization')

    def remember(self, request):
        return []

    def forget(self, request):
        return []


def get_app(settings, with_acl=False):
    """
    Return a wsgi application that use the gandi_pyramid_prometheus plugin
    """

    from pyramid.config import Configurator
    from pyramid.response import Response

    def hello_world(request):
        time.sleep(0.002)
        return Response('Hello {}!'.format(request.matchdict['name']))

    with Configurator(settings=settings) as config:

        if with_acl:
            config.set_root_factory(Context)
            config.set_authorization_policy(ACLAuthorizationPolicy())
            config.set_authentication_policy(AuthenticationPolicy())

        config.include('gandi_pyramid_prometheus')
        config.add_route('hello', '/hello/{name}')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
    return app


class MetricsTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None
        settings = {
            'prometheus.pyramid_request.buckets': '0.001, 0.1'
        }
        app = get_app(settings)
        self.app = TestApp(app)

    def tearDown(self):
        self.app = None
        if prom.pyramid_request:
            REGISTRY.unregister(prom.pyramid_request)
            prom.pyramid_request = None

        if prom.pyramid_request_ingress:
            REGISTRY.unregister(prom.pyramid_request_ingress)
            prom.pyramid_request_ingress = None

    def test_integration(self):
        self.app.get('/hello/World')
        self.app.post('/hello/Chris')
        self.app.post('/hello/McDonough')

        resp = self.app.get('/metrics')

        metrics = {
            metric.name: metric
            for metric in text_string_to_metric_families(resp.text)
        }

        pyramid_request_ingress = {
            (sample.labels['method'],
             sample.labels['path_info_pattern']): sample.value
            for sample in metrics['pyramid_request_ingress'].samples
        }

        self.assertEqual(
            pyramid_request_ingress[('GET', '/hello/{name}')],
            0.0,  # The metrics calls done during the tests is here
            )
        self.assertEqual(
            pyramid_request_ingress[('POST', '/hello/{name}')],
            0.0,
            )
        self.assertEqual(
            pyramid_request_ingress[('GET', '/metrics')],
            1.0,  # The metrics calls done during the tests is here
            )

        request_bucket = {
            (sample.labels['method'],
             sample.labels['path_info_pattern'],
             sample.labels['status'],
             sample.labels['le'],
             ): sample.value
            for sample in metrics['pyramid_request'].samples
            if sample.name == 'pyramid_request_bucket'
        }

        self.assertEqual(
            request_bucket[(u'GET', u'/hello/{name}', u'200', u'0.001')],
            0.0
        )
        self.assertEqual(
            request_bucket[(u'GET', u'/hello/{name}', u'200', u'0.1')],
            1.0
        )
        self.assertEqual(
            request_bucket[(u'GET', u'/hello/{name}', u'200', u'+Inf')],
            1.0
        )

        self.assertEqual(
            request_bucket[(u'POST', u'/hello/{name}', u'200', u'0.001')],
            0.0
        )
        self.assertEqual(
            request_bucket[(u'POST', u'/hello/{name}', u'200', u'0.1')],
            2.0
        )
        self.assertEqual(
            request_bucket[(u'POST', u'/hello/{name}', u'200', u'+Inf')],
            2.0
        )

        self.assertNotIn(
            (u'GET', u'/metrics', u'200', u'+Inf'),
            request_bucket,
            "The metrics route has not been call before the capture, "
            "and should bot be present"
        )

        # rescrape to get the previous metrics happen
        resp = self.app.get('/metrics')

        metrics = {
            metric.name: metric
            for metric in text_string_to_metric_families(resp.text)
        }
        request_bucket = {
            (sample.labels['method'],
             sample.labels['path_info_pattern'],
             sample.labels['status'],
             sample.labels['le'],
             ): sample.value
            for sample in metrics['pyramid_request'].samples
            if sample.name == 'pyramid_request_bucket'
        }

        self.assertIn(
            (u'GET', u'/metrics', u'200', u'+Inf'), request_bucket)

        request_count = {
            (sample.labels['method'],
             sample.labels['path_info_pattern'],
             sample.labels['status'],
             ): sample.value
            for sample in metrics['pyramid_request'].samples
            if sample.name == 'pyramid_request_count'
        }
        self.assertEqual(
            request_count,
            {(u'POST', u'/hello/{name}', u'200'): 2.0,
             (u'GET', u'/hello/{name}', u'200'): 1.0,
             (u'GET', u'/metrics', u'200'): 1.0,
             }
        )


class SecurityTestCase(TestCase):

    def setUp(self):
        settings = {
            'pyramid.debug_authorization': 'true',
            'prometheus.metrics_path_info': '/obfuscated',
            'prometheus.pyramid_request.buckets': '0.001, 0.1'
        }
        app = get_app(settings, with_acl=True)
        self.app = TestApp(app)

    def tearDown(self):
        self.app = None
        if prom.pyramid_request:
            REGISTRY.unregister(prom.pyramid_request)
            prom.pyramid_request = None

        if prom.pyramid_request_ingress:
            REGISTRY.unregister(prom.pyramid_request_ingress)
            prom.pyramid_request_ingress = None

    def test_403(self):
        resp = self.app.get('/obfuscated', expect_errors=True)
        self.assertEqual(resp.status_code, 403)

    def test_200(self):
        resp = self.app.get(
            '/obfuscated', headers={'Authorization': 'Bearer prometheus'})
        self.assertEqual(resp.status_code, 200)
