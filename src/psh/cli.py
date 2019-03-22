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

from psh import _common, _mutators


@attr.s
class Config:
    """Configuration for psh"""

    write = attr.ib(default=True, type=bool)


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
    default=True,
    is_flag=True,
    help="Overwrite existing setup or print to stdout",
)
def cli(no_write):
    """Top level entrypoint"""
    config.write = not no_write


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument("dependency", type=str)
def add_install(filename, dependency):
    """add a dependency to install_requires"""
    setupfile, encoding = _common.load_file(filename)
    try:
        tree = _common.parse_string(setupfile, python_grammar)
    except ParseError as pe:
        print(pe.context)
    else:
        _mutators.add_arg_to_install(tree, dependency)
        write_output(tree, filename, encoding)
