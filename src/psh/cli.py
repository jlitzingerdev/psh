"""
Copyright 2019 Jason Litzinger
"""
# pylint: disable=no-member
import os


from lib2to3.pygram import (
    python_grammar,
    python_grammar_no_print_statement,
    python_symbols,
)
from lib2to3.pgen2.parse import ParseError


import click

from psh import _common, _mutators


def write_output(tree, original, overwrite=False) -> None:
    """Write the modified output"""
    if not overwrite:
        with open("wtf.py", "w") as of:
            of.write(str(tree))


@click.group()
def cli():
    """Top level entrypoint"""


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
        write_output(tree, filename)
