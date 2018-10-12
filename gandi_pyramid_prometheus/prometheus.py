""" Declare everything related to prometheus metrics here """

import atexit
import os
from prometheus_client import Histogram, Gauge
from prometheus_client.multiprocess import mark_process_dead

from pyramid.tweens import EXCVIEW
from pyramid.settings import asbool

IS_MULTIPROC = False

pyramid_request = None
pyramid_request_ingress = None


def includeme(config):

    global IS_MULTIPROC, pyramid_request, pyramid_request_ingress

    settings = config.registry.settings

    IS_MULTIPROC = asbool(config.registry.settings.get(
        'prometheus.use_multiproc', 'false'))

    kwargs = {
        'labelnames': ['method', 'path_info_pattern'],
    }

    if IS_MULTIPROC:
        atexit.register(mark_process_dead, os.getpid())
        kwargs['multiprocess_mode'] = settings.get(
            'prometheus.pyramid_request_ingress.multiprocess_mode',
            'livesum')

    pyramid_request_ingress = Gauge(
        'pyramid_request_ingress',
        'Number of requests currrently processed',
        **kwargs)

    kwargs = {
        'labelnames': ['method', 'status', 'path_info_pattern']
    }
    if 'prometheus.pyramid_request.buckets' in settings:
        buckets = settings.get('prometheus.pyramid_request.buckets')
        buckets = buckets.replace(' ', '').split(',')
        kwargs['buckets'] = [float(buck) for buck in buckets]

    pyramid_request = Histogram(
        'pyramid_request',
        'HTTP Requests',
        **kwargs
        )
