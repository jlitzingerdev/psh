"""
Copyright 2019 Jason Litzinger
"""
# pylint: disable=no-member
from psh import _common


def test_quoted_string():
    """A string can be extracted from matching quotes"""
    m = _common.UNQUOTED_STRING.search("'foo'")
    assert m
    assert m.groups()[0] == "foo"

    m = _common.UNQUOTED_STRING.search('"bickey bam #"')
    assert m
    assert m.groups()[0] == "bickey bam #"


def test_dependency_name():
    """A dependency name is extracted if a version specifier exists"""
    m = _common.DEPENDENCY_NAME.search("foo==0.6.5")
    assert m
    assert m.groups()[0] == "foo"

    m = _common.DEPENDENCY_NAME.search("bar>0.6.5")
    assert m
    assert m.groups()[0] == "bar"

    m = _common.DEPENDENCY_NAME.search("bir  <0.6.5")
    assert m
    assert m.groups()[0] == "bir"

    m = _common.DEPENDENCY_NAME.search("detsiwt<=  18.09")
    assert m
    assert m.groups()[0] == "detsiwt"
