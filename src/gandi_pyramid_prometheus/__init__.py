from importlib import metadata

__version__ = metadata.version("pyramid_blacksmith")


def includeme(config):
    config.include(".prometheus")
    config.include(".view")
    config.include(".tweenview")
