"""
Register a pyramid tweenview that inject prometheus metrics
"""
from __future__ import absolute_import, unicode_literals

from time import time
from pyramid.tweens import EXCVIEW
from pyramid.interfaces import IRoutesMapper

from . import prometheus as prom


def get_pattern(request):
    path_info_pattern = ''
    if request.matched_route is None:
        routes_mapper = request.registry.queryUtility(IRoutesMapper)
        if routes_mapper:
            info = routes_mapper(request)
            if info and info['route']:
                path_info_pattern = info['route'].pattern
    else:
        path_info_pattern = request.matched_route.pattern
    return path_info_pattern


def histo_tween_factory(handler, registry):

    def tween(request):

        if prom.pyramid_request_ingress:
            gauge_labels = {
                'method': request.method,
                'path_info_pattern': get_pattern(request),
            }
            prom.pyramid_request_ingress.labels(**gauge_labels).inc()

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
            if prom.pyramid_request_ingress:
                prom.pyramid_request_ingress.labels(**gauge_labels).dec()

    return tween


def includeme(config):
    config.add_tween(
        'gandi_pyramid_prometheus.tweenview.histo_tween_factory', over=EXCVIEW)
