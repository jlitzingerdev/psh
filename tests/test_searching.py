"""
Copyright 2019 Jason Litzinger

"""
# pylint: disable=no-member
from lib2to3.pygram import python_grammar, python_symbols
from lib2to3.pgen2 import token

from psh import _searching, _common

TRAILING_COMMA = """
setup(install_requires=[
    "foo",
    "biz",
],
tester=[1,2,3],
)
"""


def test_trailing_comma():
    """A trailing comma is properly detected"""
    tree = _common.parse_string(TRAILING_COMMA, python_grammar)
    target = None
    for a in _searching.iterate_kinds_all(tree, (python_symbols.atom,)):
        if _searching.is_argument_atom(a, _searching.ARG_INSTALL_REQUIRES):
            target = a
    target = _searching.find_first_of_type(
        target, (token.STRING, python_symbols.listmaker)
    )
    assert _searching.trailing_comma(target)


IR_1 = """
setup(
name="foo",
install_requires=[
    "foo",
    "biz",
],
extras_require={"dev": ["blech"]},
)
"""


def test_find_install_requires():
    """Install requires is correctly located"""
    tree = _common.parse_string(TRAILING_COMMA, python_grammar)
    setup_args = _searching.find_setup_args(tree)
    ir = _searching.find_install_requires(setup_args)
    assert ir.children[0].type == token.NAME
    assert ir.children[0].value == _searching.ARG_INSTALL_REQUIRES
