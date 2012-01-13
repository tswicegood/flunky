__version_parts__ = ("0", "1", "0alpha", "0")
__version__ = ".".join(__version_parts__)


def version():
    return "%%(prog)s version %s" % __version__