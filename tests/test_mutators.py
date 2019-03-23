"""
Copyright 2019 Jason Litzinger

"""
# pylint: disable=no-member
from lib2to3.pygram import python_grammar

import pytest

from psh import _common, _mutators

NO_IR_PRE = """
setup(name="bar")
"""

NO_IR_POST = """
setup(name="bar",install_requires=["baz"])
"""


def test_add_install_nothing():
    """If no install requires argument exists, one is added."""
    tree = _common.parse_string(NO_IR_PRE, python_grammar)
    _mutators.add_arg_to_install(tree, "baz")
    assert str(tree) == NO_IR_POST


EMPTY_IR_PRE = """
setup(name="bar")
"""

EMPTY_IR_POST = """
setup(name="bar",install_requires=["rugz"])
"""


def test_add_to_empty():
    """Adding to and empty install requires inserts an entry"""
    tree = _common.parse_string(EMPTY_IR_PRE, python_grammar)
    _mutators.add_arg_to_install(tree, "rugz")
    assert str(tree) == EMPTY_IR_POST


ONE_IR_PRE = """
setup(name="bar", install_requires=["biz"],
extras_require={'dev': ['back'],
})
"""

ONE_IR_POST = """
setup(name="bar", install_requires=["biz","barg==0.7.8"],
extras_require={'dev': ['back'],
})
"""


def test_add_install_one_exists():
    """Arguments are successfully added to an install_requires list of one"""
    tree = _common.parse_string(ONE_IR_PRE, python_grammar)
    _mutators.add_arg_to_install(tree, "barg==0.7.8")
    assert ONE_IR_POST == str(tree), print(str(tree))


IR_PRE = """
setup(name="bar", install_requires=["biz", "buzz"],
extras_require={'dev': ['back'],
})
"""

IR_POST = """
setup(name="bar", install_requires=["biz", "buzz","foo"],
extras_require={'dev': ['back'],
})
"""


def test_add_install_to_many():
    """Arguments can be added to an existing list of > 1"""
    tree = _common.parse_string(IR_PRE, python_grammar)
    _mutators.add_arg_to_install(tree, "foo")
    assert IR_POST == str(tree)


def test_add_install_exists():
    """Arguments can be added to an existing list of > 1"""
    tree = _common.parse_string(IR_PRE, python_grammar)
    with pytest.raises(_mutators.AlreadyExistsError):
        _mutators.add_arg_to_install(tree, "buzz==0.3.4")
    assert IR_PRE == str(tree)
