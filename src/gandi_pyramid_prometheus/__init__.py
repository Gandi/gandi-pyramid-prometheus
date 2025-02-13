from importlib import metadata

__version__ = metadata.version("gandi_pyramid_prometheus")


def includeme(config):
    config.include(".prometheus")
    config.include(".view")
    config.include(".tweenview")
