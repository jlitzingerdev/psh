"""
Copyright 2019 Jason Litzinger
"""
# pylint: disable=no-member
import sys


from lib2to3.pygram import (
    python_grammar,
    python_grammar_no_print_statement,
    python_symbols,
)
from lib2to3.pgen2.parse import ParseError

import attr
import click

from psh import _common, _mutators, _searching


@attr.s
class Config:
    """Configuration for psh"""

    write = attr.ib(default=True, type=bool)
    filename = attr.ib(default="", type=str)


config = Config()


def write_output(tree, original, encoding) -> None:
    """Write the modified output"""
    if not config.write:
        sys.stdout.write(str(tree))
    else:
        with open(original, "wb") as f:
            f.write(str(tree).encode(encoding))


@click.group()
@click.option(
    "--no-write",
    "-n",
    default=False,
    is_flag=True,
    help="Overwrite existing setup or print to stdout",
)
@click.option(
    "--filename",
    "-f",
    default="setup.py",
    type=click.Path(exists=True),
    help="Filename to manipulate, defaults to setup.py",
)
def cli(no_write, filename):
    """Top level entrypoint"""
    config.write = not no_write
    config.filename = filename


@cli.command()
@click.argument("dependency", type=str)
def add_install(dependency):
    """Add a dependency to install_requires.  This will add an entry to the
    install_requires list.  It will not abide by any formatting standards, it
    simply adds a new item at the end.

    Usage: psh add-install setup.py mynewdependency

    If a specific version is required, use the same syntax as with pip, e.g.

    psh add-install setup.py foo>=0.4.5

    If the dependency exists in any form, no update is made.

    :param filename: The filename to update, if -n not specified.

    :param dependency: The dependency to add.
    """
    setupfile, encoding = _common.load_file(config.filename)
    try:
        tree = _common.parse_string(setupfile, python_grammar)
    except ParseError as pe:
        print(pe.context)
    else:
        try:
            _mutators.add_arg_to_install(tree, dependency)
        except _mutators.AlreadyExistsError as e:
            print("{}, not modifying".format(str(e)))
        else:
            write_output(tree, config.filename, encoding)


@cli.command()
@click.argument("new_version", required=False, type=str, default=None)
def version(new_version):
    """Get or modify the version"""
    setupfile, encoding = _common.load_file(config.filename)
    try:
        tree = _common.parse_string(setupfile, python_grammar)
    except ParseError as pe:
        print(pe.context)
    else:
        try:
            version_node = _searching.get_version(tree)
        except _common.NodeNotFoundError:
            if new_version:
                version_node = _mutators.add_version(tree)
            else:
                current_version = "There doesn't seem to be a version specification"
        else:
            current_version = _common.UNQUOTED_STRING.match(
                version_node.value
            ).groups()[0]

        if new_version:
            version_node.value = _common.quote_string(new_version)
            write_output(tree, config.filename, encoding)
        else:
            print(current_version)
