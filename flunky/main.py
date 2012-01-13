import argparse
from clint import textui
from pkg_resources import iter_entry_points
import sys

from . import version


parser = argparse.ArgumentParser(
        description="Because everyone wants a flunky")
parser.add_argument("--version", action="version", version=version())
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


def list_of_templates(sorted=False):
    templates = {}
    for entry_point in iter_entry_points(group="flunky.templates"):
        # TODO: is this needed?
        if entry_point.name in templates:
            continue

        m = entry_point.load()
        templates[entry_point.name] = {
            "description": m.__doc__.strip(),
            "path": m.__path__[0],
        }
    # TODO: add ability to sort list
    return templates


def display_installed_templates():
    templates = list_of_templates(sorted=True)
    textui.puts("Installed Flunky Templates")
    with textui.indent(2):
        for template, data in templates.items():
            textui.puts("%s - %s" % (template.ljust(10), data["description"]))
