"""
Copyright 2019 Jason Litzinger

Functions for various mutations of the parse tree.

"""
# pylint: disable=no-member
from lib2to3 import pytree
from lib2to3.pygram import (
    python_grammar,
    python_grammar_no_print_statement,
    python_symbols,
)
from lib2to3.pgen2 import token

from psh import _common, _searching


class AlreadyExistsError(Exception):
    """The desired node or leaf already exists"""


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
        if child.type == python_symbols.atom:
            append_entry_to_atom(child, dependency)


def add_arg_install_requires(trailer):
    """Create an install requires argument where none exists"""
    install_requires = pytree.Node(
        python_symbols.argument,
        [
            pytree.Leaf(1, _searching.ARG_INSTALL_REQUIRES),
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
        if target.type == python_symbols.argument:
            new = pytree.Node(python_symbols.arglist, [])
            old = target.clone()
            new.append_child(old)
            target.replace(new)
            target = new

        target.append_child(pytree.Leaf(token.COMMA, ","))
        target.append_child(install_requires)

    return install_requires


def add_arg_to_install(tree, dependency: str):
    """Add an argument to setup(install_requires, creating if necessary

    :param tree: The parse tree

    :param dependency: The dependency to add.

    """
    try:
        install_requires_node = _searching.find_install_requires(tree)
    except _common.NodeNotFoundError:
        setup_args = _searching.find_setup_args(tree)
        install_requires_node = add_arg_install_requires(setup_args)
    else:

        for ch in _searching.iterate_kinds_all(install_requires_node, (token.STRING,)):
            m = _common.UNQUOTED_STRING.search(ch.value)
            if not m:
                continue

            existing = m.groups()[0].strip()
            m = _common.DEPENDENCY_NAME.search(existing)
            if not m:
                continue
            ename = m.groups()[0].strip()

            m = _common.DEPENDENCY_NAME.search(dependency)
            if not m:
                continue
            dname = m.groups()[0].strip()

            if ename == dname:
                raise AlreadyExistsError(
                    "{} already exists as {}".format(dependency, existing)
                )

    dependency = '"{}"'.format(dependency)
    append_to_install_requires(install_requires_node, dependency)
