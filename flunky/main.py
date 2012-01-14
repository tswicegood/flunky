import argparse
from clint import textui
from pkg_resources import iter_entry_points
import sys

from . import version


parser = argparse.ArgumentParser(
        description="Because everyone wants a flunky")
parser.add_argument("--version", action="version", version=version)
parser.add_argument("package", nargs="?",
                    help="Name of the package you want to create")
parser.add_argument("--list-templates", action="store_true",
                    help="List all installed templates")


def main():
    args, argv = parser.parse_known_args()
    if args.list_templates:
        return display_installed_templates()

    if not args.package:
        parser.print_usage()


class Template(object):
    def __init__(self, entry_point):
        self.entry_point = entry_point
        self.template = entry_point.load()

    @property
    def name(self):
        return self.entry_point.name

    @property
    def description(self):
        return self.template.__doc__.strip()

    @property
    def path(self):
        return self.template.__path__[0]


def list_of_templates():
    for entry_point in iter_entry_points(group="flunky.templates"):
        yield Template(entry_point)


def display_installed_templates():
    templates = list_of_templates()
    textui.puts("Installed Flunky Templates")
    with textui.indent(2):
        for template in list_of_templates():
            textui.puts("%s - %s" % (template.name.ljust(10), template.description))
