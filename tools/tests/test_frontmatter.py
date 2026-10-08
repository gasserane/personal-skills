import pytest

from skillpub.frontmatter import parse, set_field
from skillpub.paths import PublishError


def test_set_field_replaces_existing_line_only():
    t = "---\nname: a\ndescription: d\n---\nbody\n"
    assert set_field(t, "name", "a-draft") == "---\nname: a-draft\ndescription: d\n---\nbody\n"


def test_set_field_appends_missing_key_and_keeps_crlf():
    t = "---\r\nname: a\r\ndescription: d\r\n---\r\nbody\r\n"
    assert set_field(t, "disable-model-invocation", "true") == (
        "---\r\nname: a\r\ndescription: d\r\ndisable-model-invocation: true\r\n---\r\nbody\r\n")


def test_set_field_does_not_touch_a_longer_key():
    t = "---\nnames: x\nname: a\n---\n"
    assert set_field(t, "name", "b") == "---\nnames: x\nname: b\n---\n"


def test_parse_reads_folded_description():
    assert parse("---\nname: a\ndescription: >\n  two\n  lines\n---\n")["description"].strip() == "two lines"


def test_parse_rejects_missing_frontmatter():
    with pytest.raises(PublishError, match="no frontmatter"):
        parse("no frontmatter here\n")
