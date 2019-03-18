"""
Copyright 2019 Jason Litzinger

Helpers for searching the parse tree
"""
# pylint: disable=no-member

import typing

from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import (
    python_grammar,
    python_grammar_no_print_statement,
    python_symbols,
)
from lib2to3.pgen2 import driver, token


from psh import _common


class TypeNotFoundError(Exception):
    """Error when an expected token/symbol not found"""


def is_call(n, function_name):
    """Look for a matching function call"""
    if n.type != python_symbols.power:
        return False
    if n.children[1].type != python_symbols.trailer:
        return False
    if n.children[0].type != token.NAME:
        return False
    if n.children[0].value != function_name:
        return False
    return True


def find_argument_in_arglist(args, target):
    """Locate an argument in an argument list or a single argument."""
    for child in args.children:
        # args is really a python_symbols.argument
        if child.type == token.NAME and child.value == target:
            return child
        if child.type != python_symbols.argument:
            continue
        if child.children[0].value == target:
            return child
    raise _common.NodeNotFoundError("No argument {} in arglist".format(target))


def find_first_of_type(parent, kinds) -> typing.Union[Leaf, Node]:
    """Find the first child whose type is in kinds"""
    for ch in parent.children:
        if ch.type in kinds:
            return ch
    raise TypeNotFoundError("No matches for {}".format(kinds))
