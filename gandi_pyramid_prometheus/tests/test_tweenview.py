from pyramid import testing
from pyramid.response import Response
from prometheus_client import REGISTRY

from gandi_pyramid_prometheus import prometheus as prom
from gandi_pyramid_prometheus import tweenview

from .base import TestCase


class DummyRoute(object):
    pattern = '/bars/{id}'


def view(req):
    return Response()


class PromTestCase(TestCase):

    def test_histo_tween_factory(self):
        prom.includeme(self.conf)

        tween = tweenview.histo_tween_factory(view, self.conf.registry)

        req = testing.DummyRequest(matched_route=DummyRoute())
        tween(req)

        inf = REGISTRY.get_sample_value(
            'pyramid_request_bucket',
            {'path_info_pattern': '/bars/{id}',
             'method': 'GET',
             'le': '+Inf',
             'status': '200'},)
        self.assertEqual(inf, 1.)

        ingress = REGISTRY.get_sample_value(
            'pyramid_request_ingress',
            {'path_info_pattern': '/bars/{id}',
             'method': 'GET',
             },)

        self.assertEqual(ingress, 0.)
