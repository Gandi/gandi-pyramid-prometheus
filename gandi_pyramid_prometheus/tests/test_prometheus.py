
from gandi_pyramid_prometheus import prometheus as prom
from prometheus_client import Gauge, Histogram

from .base import TestCase


class PromTestCase(TestCase):

    def test_includeme(self):

        self.assertIsNone(prom.pyramid_request)
        self.assertIsNone(prom.pyramid_request_ingress)

        prom.includeme(self.conf)

        self.assertIsNotNone(prom.pyramid_request)
        self.assertIsNotNone(prom.pyramid_request_ingress)

        self.assertEqual(prom.pyramid_request._type, 'histogram')
        self.assertIsNotNone(prom.pyramid_request_ingress._type, 'gauge')
