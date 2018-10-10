import os
import unittest
from pyramid import testing

from gandi_pyramid_prometheus import prometheus as prom


here = os.path.abspath(os.path.dirname(__file__))
prometheus_multiproc_dir = os.path.join(here, 'multiproc_dir')
os.environ['prometheus_multiproc_dir'] = prometheus_multiproc_dir

from prometheus_client import Gauge, Histogram, REGISTRY


class TestCase(unittest.TestCase):

    def setUp(self):
        self.conf = testing.setUp(settings={
            'prometheus.pyramid_request.buckets': '0.5,1.,2.'
        })

    def tearDown(self):
        testing.tearDown()

        if prom.pyramid_request:
            REGISTRY.unregister(prom.pyramid_request)
            prom.pyramid_request = None

        if prom.pyramid_request_ingress:
            REGISTRY.unregister(prom.pyramid_request_ingress)
            prom.pyramid_request_ingress = None
