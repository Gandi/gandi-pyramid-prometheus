"""
Register a pyramid tweenview that inject prometheus metrics
"""
from __future__ import absolute_import, unicode_literals

from time import time
from pyramid.tweens import EXCVIEW, INGRESS

from . import prometheus as prom


def get_pattern(request):
    if request.matched_route is None:
        path_info = ''
    else:
        path_info = request.matched_route.pattern
    return path_info


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
                    path_info=get_pattern(request),
                    status=status,
                    ).observe(duration)

    return tween


def inprocess_tween_factory(handler, registry):
    def tween(request):
        labels = {
            'method': request.method,
            'path_info': get_pattern(request),
        }

        if prom.pyramid_request_inprocess:
            prom.pyramid_request_inprocess.labels(**labels).inc()
        try:
            response = handler(request)
            status = str(response.status_int)
            return response
        finally:
            if prom.pyramid_request_inprocess:
                prom.pyramid_request_inprocess.labels(**labels).dec()
    return tween


def includeme(config):
    config.add_tween(
        'gandi_pyramid_prometheus.tweenview.histo_tween_factory', over=EXCVIEW)
    config.add_tween(
        'gandi_pyramid_prometheus.tweenview.inprocess_tween_factory',
        under=INGRESS)
