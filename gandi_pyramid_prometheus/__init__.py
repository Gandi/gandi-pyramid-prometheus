from __future__ import absolute_import, unicode_literals

__version__ = '0.3'


def includeme(config):
    config.include('.prometheus')
    config.include('.view')
    config.include('.tweenview')
