import argparse
from clint import textui
from os.path import exists
from os.path import join
import os
from pkg_resources import iter_entry_points
import sys
import shutil
import textwrap

from . import version


parser = argparse.ArgumentParser(
        description="Because everyone wants a flunky")
parser.add_argument("--version", action="version", version=version)
parser.add_argument("package", nargs="?",
                    help="Name of the package you want to create")
parser.add_argument("--list-templates", action="store_true",
                    help="List all installed templates")
parser.add_argument("--template", action="store", default="basic")


def main():
    args, argv = parser.parse_known_args()
    if args.list_templates:
        return display_installed_templates()

    if not args.package:
        parser.print_usage()

    template = find_template(args.template)
    template.create(args.package)


class Template(object):
    # TODO: use logger/reporter for output
    def __init__(self, name, template):
        self.name = name
        self.template = template

    @property
    def description(self):
        return self.template.__doc__.strip()

    @property
    def source_dir(self):
        return self.template.__path__[0]

    @property
    def default_init(self):
        if hasattr(self.template, "default_init"):
            return self.template.default_init
        return textwrap.dedent("""
            from pkgutil import extend_path
            __path__ = extend_path(__path__, __name__)
        """).strip()

    def is_excluded(self, file_name):
        if not hasattr(self.template, "ignored_files"):
            return False
        if file_name.endswith(".pyc"):
            return True
        for ignore in self.template.ignored_files:
            # TODO: support regular expressions
            if file_name.endswith(ignore):
                return True
        return False

    def add_default_inits(self, destination, package):
        if package.find(".") is -1:
            return
        current_level = ""
        for level in package.split(".")[:-1]:
            current_level = join(current_level, level)
            with open(join(destination, current_level, "__init__.py"), "w") as f:
                f.write(self.default_init)

    def copy_files_into_location(self, module_dir, destination):
        source_module = join(self.source_dir, "package")

        def files():
            for dirpath, dirnames, filenames in os.walk(self.source_dir):
                if dirpath.find("package") is not -1:
                    continue
                for dirname in dirnames:
                    if dirname == "package":
                        continue
                    a = os.path.join(dirpath, dirname)
                    if self.is_excluded(a):
                        continue
                    yield a
                for name in filenames:
                    a = os.path.join(dirpath, name)
                    if name.endswith(".pyc") or self.is_excluded(a):
                        continue
                    yield a
            for a in os.listdir(self.source_dir):
                if a.startswith("__init__.py"):
                    continue
                name = join(self.source_dir, a)
                if self.is_excluded(name) or os.path.isdir(name):
                    continue
                yield name

        def package_files():
            for dirpath, dirnames, filenames in os.walk(source_module):
                for dirname in dirnames:
                    a = os.path.join(dirpath, dirname)
                    if self.is_excluded(a):
                        continue
                    yield a
                for name in filenames:
                    a = os.path.join(dirpath, name)
                    if name.endswith(".pyc") or self.is_excluded(a):
                        continue
                    yield a

        for file_name in package_files():
            dest_name = file_name.replace(source_module, module_dir)
            if os.path.isdir(file_name):
                os.mkdir(dest_name)
            else:
                # TODO: template
                # TODO: handle utf-8
                shutil.copy(file_name, dest_name)

        for file_name in files():
            dest_name = file_name.replace(self.source_dir, destination)
            if os.path.isdir(file_name):
                os.mkdir(dest_name)
            else:
                # TODO: template
                # TODO: handle utf-8
                shutil.copy(file_name, dest_name)

    def create(self, package):
        textui.puts("Creating package %s" % package)
        destination = join(os.getcwd(), package)
        if exists(destination):
            textui.puts_err("Package already exists!")
            return

        module_dir = join(destination, package.replace(".", "/"))
        os.makedirs(module_dir)

        if package.find(".") is not -1:
            self.add_default_inits(destination, package)

        self.copy_files_into_location(module_dir, destination)


def list_of_templates():
    for entry_point in iter_entry_points(group="flunky.templates"):
        yield Template(entry_point.name, entry_point.load())


def find_template(name):
    # TODO: Make this suck less
    for t in list_of_templates():
        if t.name == name:
            return t


def display_installed_templates():
    templates = list_of_templates()
    textui.puts("Installed Flunky Templates")
    with textui.indent(2):
        for template in list_of_templates():
            textui.puts("%s - %s" % (template.name.ljust(10), template.description))
