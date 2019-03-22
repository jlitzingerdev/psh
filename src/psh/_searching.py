"""
Copyright 2019 Jason Litzinger

Helpers for searching the parse tree for general and setup specific targets.
"""
# pylint: disable=no-member

import typing

from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import (
    python_grammar,
    python_grammar_no_print_statement,
    python_symbols,
)
from lib2to3.pgen2 import token


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


def is_call_trailer(n, function_name):
    """Look for a matching function call"""
    if n.type != python_symbols.trailer:
        return False
    if n.parent.type != python_symbols.power:
        return False
    if n.parent.children[0].type != token.NAME:
        return False
    if n.parent.children[0].value != function_name:
        return False
    return True


def is_argument_atom(n, name):
    """Determine if this is an atom for a specific argument"""
    if n.parent.type != python_symbols.argument:
        return False

    if n.parent.children[0].type != token.NAME:
        return False

    if n.parent.children[0].value != name:
        return False

    return True


def find_argument_in_arglist(args, target):
    """Locate an argument in an argument list or a single argument."""
    for child in args.children:
        # args is really a python_symbols.argument
        if child.type == token.NAME and child.value == target:
            return args
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


def iterate_kinds_children(parent, kinds):
    """Generator for a specific type node in children"""
    return (ch for ch in parent.children if ch.type in kinds)


def iterate_kinds_all(parent, kinds):
    """Generator for a specific type of node for entire subtree"""
    for ch in parent.pre_order():
        if ch.type in kinds:
            yield ch


def trailing_comma(node):
    """Determine if there is a trailing comma"""
    if node.children:
        return node.children[-1].type == token.COMMA
    return False


ARG_INSTALL_REQUIRES = "install_requires"
ARGUMENT_LIST = (python_symbols.argument, python_symbols.arglist)


def find_setup_args(tree):
    """Locate the setup function trailer node"""
    for n in tree.pre_order():
        if is_call_trailer(n, "setup"):
            return n
    raise _common.NodeNotFoundError("unable to locate setup")


def find_install_requires(tree):
    """Locate the install requires argument"""
    for n in iterate_kinds_all(tree, (python_symbols.trailer,)):
        name_candidate = n.parent.children[0]
        if name_candidate.type == token.NAME and name_candidate.value == "setup":
            try:
                for candidate in iterate_kinds_children(n, ARGUMENT_LIST):
                    return find_argument_in_arglist(candidate, ARG_INSTALL_REQUIRES)
            except _common.NodeNotFoundError:
                continue

    raise _common.NodeNotFoundError("no install_requires argument")
