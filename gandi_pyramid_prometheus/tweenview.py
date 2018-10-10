"""
Register a pyramid tweenview that inject prometheus metrics
"""
from __future__ import absolute_import, unicode_literals

from time import time
from pyramid.tweens import EXCVIEW, INGRESS

from . import prometheus as prom


def get_pattern(request):
    if request.matched_route is None:
        path_info_pattern = ''
    else:
        path_info_pattern = request.matched_route.pattern
    return path_info_pattern


def histo_tween_factory(handler, registry):

    def tween(request):

        start = time()
        status = '500'
        try:
            response = handler(request)
            status = str(response.status_int)
            return response
        finally:
            duration = time() - start
            if prom.pyramid_request:
                prom.pyramid_request.labels(
                    method=request.method,
                    path_info_pattern=get_pattern(request),
                    status=status,
                    ).observe(duration)

    return tween


def ingress_tween_factory(handler, registry):
    def tween(request):
        labels = {
            'method': request.method,
            'path_info_pattern': get_pattern(request),
        }

        if prom.pyramid_request_ingress:
            prom.pyramid_request_ingress.labels(**labels).inc()
        try:
            response = handler(request)
            status = str(response.status_int)
            return response
        finally:
            if prom.pyramid_request_ingress:
                prom.pyramid_request_ingress.labels(**labels).dec()
    return tween


def includeme(config):
    config.add_tween(
        'gandi_pyramid_prometheus.tweenview.histo_tween_factory', over=EXCVIEW)
    config.add_tween(
        'gandi_pyramid_prometheus.tweenview.ingress_tween_factory',
        under=INGRESS)
