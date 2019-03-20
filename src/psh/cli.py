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

from psh import _common, _searching


ARGUMENT_LIST = (python_symbols.argument, python_symbols.arglist)


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


def find_setup_call(tree):
    """Locate the setup function arglist node"""
    for n in tree.pre_order():
        if _searching.is_call(n, "setup"):
            return n
    raise _common.NodeNotFoundError("unable to locate setup")


ARG_INSTALL_REQUIRES = "install_requires"


def find_install_requires(trailer):
    """Locate the install requires argument"""
    for candidate in _searching.iterate_kinds(trailer, ARGUMENT_LIST):
        try:
            return _searching.find_argument_in_arglist(candidate, ARG_INSTALL_REQUIRES)
        except _common.NodeNotFoundError:
            continue

    raise _common.NodeNotFoundError("no install_requires argument")


def append_entry_to_atom(atom, entry):
    """Append an entry to a list"""
    try:
        target = _searching.find_first_of_type(
            atom, (token.STRING, python_symbols.listmaker)
        )
    except _searching.TypeNotFoundError:
        atom.insert_child(-1, pytree.Leaf(token.NAME, entry))
    else:
        if target.type == token.STRING:
            context = (target.prefix, (target.lineno, target.column))
            new = pytree.Node(
                python_symbols.listmaker,
                [pytree.Leaf(token.NAME, target.value, context)],
            )
            target.replace(new)
            target = new

        if not _searching.trailing_comma(target):
            target.append_child(pytree.Leaf(token.COMMA, ","))
        target.append_child(pytree.Leaf(token.STRING, entry))


def append_to_install_requires(install_requires_node, dependency):
    """Add an entry to the install requires node"""
    for child in install_requires_node.children:
        print(dump_node(child))
        if child.type == python_symbols.atom:
            append_entry_to_atom(child, dependency)


def write_output(tree, original, overwrite=False) -> None:
    """Write the modified output"""
    if not overwrite:
        with open("wtf.py", "w") as of:
            of.write(str(tree))


def add_arg_install_requires(trailer):
    """Create an install requires argument where none exists"""
    install_requires = pytree.Node(
        python_symbols.argument,
        [
            pytree.Leaf(1, ARG_INSTALL_REQUIRES),
            pytree.Leaf(22, "="),
            pytree.Node(
                python_symbols.atom, [pytree.Leaf(9, "["), pytree.Leaf(10, "]")]
            ),
        ],
    )

    try:
        target = _searching.find_first_of_type(
            trailer, (python_symbols.argument, python_symbols.arglist)
        )
    except _searching.TypeNotFoundError:
        trailer.insert_child(1, install_requires)
    else:
        target = trailer.children[1]
        if target.type == python_symbols.argument:
            new = pytree.Node(python_symbols.arglist, [])
            old = target.clone()
            new.append_child(old)
            target.replace(new)
            target = new

        target.append_child(pytree.Leaf(token.COMMA, ","))
        target.append_child(install_requires)

    return install_requires


@click.group()
def cli():
    """Top level entrypoint"""


@cli.command()
@click.argument("filename", type=click.Path(exists=True))
@click.argument("dependency", type=str)
def add_install_requires(filename, dependency):
    """add a dependency to install_requires"""
    setupfile = load_file(filename)
    d = driver.Driver(python_grammar, pytree.convert)
    dependency = '"{}"'.format(dependency)
    try:
        tree = d.parse_string(setupfile, debug=True)
    except ParseError as pe:
        print(pe.context)
    else:
        setup_call = find_setup_call(tree)
        print(dump_node(setup_call))
        trailer = _searching.find_first_of_type(setup_call, (python_symbols.trailer,))
        try:
            install_requires_node = find_install_requires(trailer)
        except _common.NodeNotFoundError:
            install_requires_node = add_arg_install_requires(trailer)

        print("pre {}".format(dump_node(install_requires_node)))
        print("on {}".format(dump_node(trailer)))
        append_to_install_requires(install_requires_node, dependency)
        write_output(tree, filename)
