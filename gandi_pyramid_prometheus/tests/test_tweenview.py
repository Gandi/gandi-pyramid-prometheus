from pyramid import testing
from pyramid.response import Response
from prometheus_client import REGISTRY

from gandi_pyramid_prometheus import prometheus as prom
from gandi_pyramid_prometheus import tweenview

from .base import TestCase


class PromTestCase(TestCase):

    def test_histo_tween_factory(self):
        prom.includeme(self.conf)

        class DummyRoute(object):
            pattern = '/bars/{id}'

        def view(req):
            return Response()

        tween = tweenview.histo_tween_factory(view, self.conf.registry)

        req = testing.DummyRequest(matched_route=DummyRoute())
        tween(req)

        print  REGISTRY.get_sample_value('pyramid_requests')
