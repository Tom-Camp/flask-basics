import pytest
from werkzeug.datastructures import MultiDict
from wtforms import Form
from wtforms.validators import Optional

from app.forms.resume_edit_form import StringListField


class StringListForm(Form):
    items = StringListField(validators=[Optional()])


def test_string_list_loads_and_renders():
    values = ["First item", "Second item"]
    form = StringListForm(data={"items": values})

    assert form.items.data == values
    assert form.items.data is not values
    assert "<textarea" in str(form.items())
    assert "First item\nSecond item" in str(form.items())


@pytest.mark.parametrize(
    ("submitted", "expected"),
    [
        ("  First item \r\n\r\n Second item \n  ", ["First item", "Second item"]),
        (" \n\t ", []),
        ("", []),
    ],
)
def test_string_list_parses_submission(submitted, expected):
    form = StringListForm(MultiDict({"items": submitted}))

    assert form.validate()
    assert form.items.data == expected


def test_string_list_defaults_to_empty_list():
    form = StringListForm()

    assert form.items.data == []
    assert form.items._value() == ""


def test_string_list_missing_submission_clears_previous_data():
    form = StringListForm(MultiDict(), data={"items": ["Previous item"]})

    assert form.validate()
    assert form.items.data == []
