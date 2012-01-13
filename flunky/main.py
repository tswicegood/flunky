import argparse
from pkg_resources import iter_entry_points
import sys

import flunky

ENTRY_POINT = "flunky.commands"


def main():
    parser = argparse.ArgumentParser(description='Choose subcommand to run.')
    parser.add_argument('--version', action='version', version='%%(prog)s version %s' % flunky.__version__)
    subparsers = parser.add_subparsers(title='subcommands')

    loaded = {}
    for ep in iter_entry_points(group=ENTRY_POINT):
        # TODO: needed?
        if ep.name in loaded:
            continue
        loaded[ep.name] = True
        command = ep.load()
        # TODO: summary v full help text?
        command_subparser = subparsers.add_subparsers(ep.name,
                description=command.__doc__,
                help=command.__doc__)
        if hasattr(command, "build_parser"):
            command.build_parser(command_subparser)
        command_subparser.set_default(func=command)

    args, argv = parser.parse_known_args()
    kwargs = vars(args)
    # TODO: can this be None?  What should happen when it is?
    func = kwargs.pop('func', None)
    if argv:
        func(argv=argv, **kwargs)
    else:
        func(**kwargs)


