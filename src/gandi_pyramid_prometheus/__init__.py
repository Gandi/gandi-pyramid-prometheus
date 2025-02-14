try:
    from importlib.metadata import version
except ImportError:
    # python 3.7
    import pkg_resources

    def version(distribution_name: str):
        return pkg_resources.get_distribution(distribution_name).version


__version__ = version("gandi_pyramid_prometheus")


def includeme(config):
    config.include(".prometheus")
    config.include(".view")
    config.include(".tweenview")
