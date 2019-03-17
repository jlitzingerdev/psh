"""
Copyright 2019 Jason Litzinger
"""
# pylint: disable=no-member
import os
import tokenize

from lib2to3 import pytree
from lib2to3.pygram import (
    python_grammar,
    python_grammar_no_print_statement,
    python_symbols,
)
from lib2to3.pgen2 import driver, token
from lib2to3.pgen2.parse import ParseError


import click


ARGUMENT_LIST = (python_symbols.argument, python_symbols.arglist)


class NodeNotFoundError(Exception):
    """Unable to locate a matching parset tree node"""


def load_file(filename):
    """Figure out the encoding and load setup.py"""
    with open(filename, "rb") as f:
        encoding, _ = tokenize.detect_encoding(f.readline)

    return open(filename, "r", encoding=encoding).read()


def node_type(n) -> str:
    """Obtain the string type for the token"""
    if n.type <= token.NT_OFFSET:
        return token.tok_name[n.type]
    return pytree.type_repr(n.type)


def dump_node(n):
    """Print a node"""
    return "{}: {!r}".format(node_type(n), n)


def dump_tree(tree):
    """Print the entire tree in pre-order"""
    for n in tree.pre_order():
        print(dump_node(n))


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


def find_setup_call(tree):
    """Locate the setup function arglist node"""
    for n in tree.pre_order():
        if is_call(n, "setup"):
            return n
    raise NodeNotFoundError("unable to locate setup")


ARG_INSTALL_REQUIRES = "install_requires"


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
    raise NodeNotFoundError("No argument {} in arglist".format(target))


def find_install_requires(trailer):
    """Locate the install requires argument"""
    if len(trailer.children) == 1:
        raise NodeNotFoundError("no install_requires argument")

    args = trailer.children[1]
    return find_argument_in_arglist(args, ARG_INSTALL_REQUIRES)


def append_entry(atom, entry):
    """Append an entry to a list"""
    entry = '"{}"'.format(entry)
    if len(atom.children) <= 2:
        atom.insert_child(
            len(atom.children) - 1, pytree.Leaf(token.NAME, '"{}"'.format(entry))
        )
    elif atom.children[1].type == token.STRING:
        # Replace node with listmaker
        target = atom.children[1]
        context = (target.prefix, (target.lineno, target.column))
        new = pytree.Node(
            python_symbols.listmaker, [pytree.Leaf(token.NAME, target.value, context)]
        )
        target.replace(new)
        new.append_child(pytree.Leaf(token.COMMA, ","))
        new.append_child(pytree.Leaf(token.STRING, entry))
        print("post modify: {}".format(dump_node(atom)))
    else:
        listmaker = atom.children[1]
        listmaker.append_child(pytree.Leaf(token.COMMA, ","))
        listmaker.append_child(pytree.Leaf(token.STRING, entry))


@click.group()
def cli():
    """Top level entrypoint"""


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument("dependency", type=str)
def install_requires(filename, dependency):
    """dAd a dependency to install_requires"""
    setupfile = load_file(filename)
    d = driver.Driver(python_grammar, pytree.convert)
    try:
        tree = d.parse_string(setupfile, debug=True)
        # dump_tree(tree)
        n = find_setup_call(tree)
        print(dump_node(n))

        try:
            install_requires_node = find_install_requires(n.children[1])
        except NodeNotFoundError:
            print("No existing install requires")
        else:
            print(dump_node(install_requires_node))
            for child in install_requires_node.children:
                if child.type == python_symbols.atom:
                    append_entry(child, dependency)

        with open("wtf.py", "w") as of:
            of.write(str(tree))

    except ParseError as pe:
        print(pe.context)
