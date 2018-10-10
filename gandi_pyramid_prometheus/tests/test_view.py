from pyramid import testing

from gandi_pyramid_prometheus import prometheus as prom
from gandi_pyramid_prometheus.view import get_metrics

from .base import TestCase


class PromTestCase(TestCase):

    def test_get_metrics(self):
        prom.includeme(self.conf)

        req = testing.DummyRequest()

        prom.pyramid_request.labels(
            path_info_pattern='/test', method='GET', status='200'
            ).observe(.007)
        prom.pyramid_request.labels(
            path_info_pattern='/test', method='GET', status='200').observe(.7)
        prom.pyramid_request.labels(
            path_info_pattern='/test', method='GET', status='200').observe(7.)

        prom.pyramid_request_ingress.labels(
            path_info_pattern='/test', method='GET').set(42)

        metric = get_metrics(req)

        self.assertIn(
            '# HELP pyramid_request_ingress '
            'Number of requests currrently processed\n', metric.text)
        
        self.assertIn(
            '# TYPE pyramid_request_ingress gauge\n', metric.text)
        
        self.assertIn(
            'pyramid_request_ingress{method="GET",path_info_pattern="/test"} '
            '42.0\n',
            metric.text
            )

        self.assertIn(
            'pyramid_request_bucket{le="0.5",method="GET",'
            'path_info_pattern="/test",status="200"} 1.0\n',
            metric.text
            )
        self.assertIn(
            'pyramid_request_bucket{le="1.0",method="GET",'
            'path_info_pattern="/test",status="200"} 2.0\n',
            metric.text
            )
        self.assertIn(
            'pyramid_request_bucket{le="2.0",method="GET",'
            'path_info_pattern="/test",status="200"} 2.0\n',
            metric.text
            )
        self.assertIn(
            'pyramid_request_bucket{le="+Inf",method="GET",'
            'path_info_pattern="/test",status="200"} 3.0\n',
            metric.text
            )
