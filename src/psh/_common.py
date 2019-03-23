"""
Copyright 2019 Jason Litzinger
"""
# pylint: disable=no-member
import tokenize
import typing
from lib2to3 import pytree
from lib2to3.pgen2 import driver, token
import re


UNQUOTED_STRING = re.compile("[\"|'](.*)[\"|']")


class NodeNotFoundError(Exception):
    """Unable to locate a matching parset tree node"""


def load_file(filename: str) -> typing.Tuple[typing.TextIO, str]:
    """Figure out the encoding and load setup.py"""
    with open(filename, "rb") as f:
        encoding, _ = tokenize.detect_encoding(f.readline)

    return open(filename, "r", encoding=encoding).read(), encoding


def parse_string(code: str, grammar):
    """Parse a tree from the code"""
    d = driver.Driver(grammar, pytree.convert)
    return d.parse_string(code, debug=True)


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
