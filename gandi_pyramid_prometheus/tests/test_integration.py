from __future__ import unicode_literals
from unittest import TestCase
import time

from webtest import TestApp
from gandi_pyramid_prometheus import prometheus as prom
from prometheus_client import REGISTRY
from prometheus_client.parser import text_string_to_metric_families


def get_app():
    """
    Return a wsgi application that use the gandi_pyramid_prometheus plugin
    """

    from pyramid.config import Configurator
    from pyramid.response import Response

    settings = {
        'prometheus.metric_path_info': '/obfuscated',
        'prometheus.pyramid_request.buckets': '0.001, 0.1'
    }

    def hello_world(request):
        time.sleep(0.002)
        return Response('Hello {}!'.format(request.matchdict['name']))

    with Configurator(settings=settings) as config:
        config.include('gandi_pyramid_prometheus')
        config.add_route('hello', '/hello/{name}')
        config.add_view(hello_world, route_name='hello')
        app = config.make_wsgi_app()
    return app


class IntegrationTestCase(TestCase):

    def setUp(self):
        self.maxDiff = None
        app = get_app()
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

        resp = self.app.get('/obfuscated')

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
            0.0, # The metrics calls done during the tests is here
            )
        self.assertEqual(
            pyramid_request_ingress[('POST', '/hello/{name}')],
            0.0,
            )
        self.assertEqual(
            pyramid_request_ingress[('GET', '/obfuscated')],
            1.0, # The metrics calls done during the tests is here
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
            (u'GET', u'/obfuscated', u'200', u'+Inf'),
            request_bucket,
            "The metrics route has not been call before the capture, "
            "and should bot be present"
        )

        # rescrape to get the previous metrics happen
        resp = self.app.get('/obfuscated')

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
            (u'GET', u'/obfuscated', u'200', u'+Inf'), request_bucket)

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
             (u'GET', u'/obfuscated', u'200'): 1.0,
             }
        )
