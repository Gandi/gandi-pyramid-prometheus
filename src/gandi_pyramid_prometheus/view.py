""" Generate a prometheus view to expose the metrics """
from __future__ import absolute_import, unicode_literals

from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.response import Response

from prometheus_client import (
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
    )
from prometheus_client.multiprocess import MultiProcessCollector

from . import prometheus as prom


def get_metrics(request):
    """Pyramid view that return the metrics"""

    if prom.IS_MULTIPROC:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)
    else:
        registry = REGISTRY

    request.response.content_type = CONTENT_TYPE_LATEST
    resp = Response(
        content_type=CONTENT_TYPE_LATEST,
        )
    resp.body = generate_latest(registry)
    return resp


def includeme(config):
    """Configure the /metrics view"""
    metrics_path_info = config.registry.settings.get(
        'prometheus.metrics_path_info', '/metrics')

    config.add_route('prometheus_metric', metrics_path_info)
    config.add_view(
        get_metrics,
        route_name='prometheus_metric',
        permission='prometheus:metric:read',
        )
