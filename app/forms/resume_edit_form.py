"""
WTForms for editing a resume stored as ``ResumeData`` (jsonresume schema).

Nested sections are ``FormField``/``FieldList`` of plain ``wtforms.Form``
subforms (only the top-level ``FlaskForm`` carries the CSRF token). Lists of
strings are edited as one item per line. Dates are picked with a date input and parsed by
``FlexDate`` in ``resume_schema``.
"""

from typing import Any

from flask_wtf import FlaskForm
from wtforms import Form
from wtforms.fields import (
    BooleanField,
    Field,
    FieldList,
    FormField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import Optional, Email, URL, Length
from wtforms.widgets import DateInput, TextArea

from app.models.resume_schema import ResumeData

_OPT = [Optional()]
_URL = [Optional(), URL(require_tld=False), Length(max=2048)]


class StringListField(Field):
    """A list[str] edited as one item per line."""

    # WTForms stubs restrict TextArea to StringField; rendering only needs _value().
    widget = TextArea()  # type: ignore[assignment]
    data: list[str]

    def process_data(self, value: list[str] | None) -> None:
        self.data = list(value or [])

    def _value(self) -> str:
        return "\n".join(self.data or [])

    def process_formdata(self, valuelist: list[str]) -> None:
        text = valuelist[0] if valuelist else ""
        self.data = [line.strip() for line in text.splitlines() if line.strip()]


class DateStringField(StringField):
    """Date kept as a string; rendered as a native date picker (YYYY-MM-DD)."""

    widget = DateInput()


class _SubForm(Form):
    """Base for nested forms; CSRF is handled by the parent FlaskForm."""


class LocationForm(_SubForm):
    address = StringField(validators=_OPT)
    postal_code = StringField(validators=_OPT)
    city = StringField(validators=_OPT)
    region = StringField(validators=_OPT)
    country_code = StringField(validators=_OPT)


class ProfileForm(_SubForm):
    network = StringField(validators=_OPT)
    username = StringField(validators=_OPT)
    url = StringField(validators=_URL)


class BasicsForm(_SubForm):
    name = StringField(validators=_OPT)
    label = StringField(validators=_OPT)
    image = StringField(validators=_URL)
    email = StringField(validators=[Optional(), Email()])
    phone = StringField(validators=_OPT)
    url = StringField(validators=_URL)
    summary = TextAreaField(validators=_OPT)
    location = FormField(LocationForm)
    profiles = FieldList(FormField(ProfileForm), min_entries=0)


class JobCategoryForm(_SubForm):
    practice_area = StringField(validators=_OPT)
    category = StringField(validators=_OPT)
    start_date = DateStringField(validators=_OPT)
    end_date = DateStringField(validators=_OPT)
    is_current = BooleanField()


class WorkForm(_SubForm):
    employer_name = StringField(validators=_OPT)
    position = StringField(validators=_OPT)
    url = StringField(validators=_URL)
    start_date = DateStringField(validators=_OPT)
    end_date = DateStringField(validators=_OPT)
    summary = TextAreaField(validators=_OPT)
    highlights = StringListField(validators=_OPT)
    categories = FieldList(FormField(JobCategoryForm), min_entries=0)


class VolunteerForm(_SubForm):
    organization = StringField(validators=_OPT)
    position = StringField(validators=_OPT)
    url = StringField(validators=_URL)
    start_date = DateStringField(validators=_OPT)
    end_date = DateStringField(validators=_OPT)
    summary = TextAreaField(validators=_OPT)
    highlights = StringListField(validators=_OPT)


class EducationForm(_SubForm):
    institution = StringField(validators=_OPT)
    url = StringField(validators=_URL)
    area = StringField(validators=_OPT)
    degree_type = StringField(validators=_OPT)
    start_date = DateStringField(validators=_OPT)
    end_date = DateStringField(validators=_OPT)
    score = StringField(validators=_OPT)
    courses = StringListField(validators=_OPT)


class AwardForm(_SubForm):
    title = StringField(validators=_OPT)
    date = DateStringField(validators=_OPT)
    awarder = StringField(validators=_OPT)
    summary = TextAreaField(validators=_OPT)


class CertificateForm(_SubForm):
    name = StringField(validators=_OPT)
    date = DateStringField(validators=_OPT)
    issuer = StringField(validators=_OPT)
    url = StringField(validators=_URL)


class PublicationForm(_SubForm):
    name = StringField(validators=_OPT)
    publisher = StringField(validators=_OPT)
    release_date = DateStringField(validators=_OPT)
    url = StringField(validators=_URL)
    summary = TextAreaField(validators=_OPT)


class SkillForm(_SubForm):
    name = StringField(validators=_OPT)
    level = StringField(validators=_OPT)
    keywords = StringListField(validators=_OPT)


class LanguageForm(_SubForm):
    language = StringField(validators=_OPT)
    fluency = StringField(validators=_OPT)


class InterestForm(_SubForm):
    name = StringField(validators=_OPT)
    keywords = StringListField(validators=_OPT)


class ReferenceForm(_SubForm):
    name = StringField(validators=_OPT)
    reference = TextAreaField(validators=_OPT)


class ProjectForm(_SubForm):
    name = StringField(validators=_OPT)
    description = TextAreaField(validators=_OPT)
    highlights = StringListField(validators=_OPT)
    keywords = StringListField(validators=_OPT)
    start_date = DateStringField(validators=_OPT)
    end_date = DateStringField(validators=_OPT)
    url = StringField(validators=_URL)
    roles = StringListField(validators=_OPT)
    company = StringField(validators=_OPT)
    job_type = StringField(validators=_OPT)


class ResumeEditForm(FlaskForm):
    basics = FormField(BasicsForm)
    work = FieldList(FormField(WorkForm), min_entries=0)
    volunteer = FieldList(FormField(VolunteerForm), min_entries=0)
    education = FieldList(FormField(EducationForm), min_entries=0)
    awards = FieldList(FormField(AwardForm), min_entries=0)
    certificates = FieldList(FormField(CertificateForm), min_entries=0)
    publications = FieldList(FormField(PublicationForm), min_entries=0)
    skills = FieldList(FormField(SkillForm), min_entries=0)
    languages = FieldList(FormField(LanguageForm), min_entries=0)
    interests = FieldList(FormField(InterestForm), min_entries=0)
    references = FieldList(FormField(ReferenceForm), min_entries=0)
    projects = FieldList(FormField(ProjectForm), min_entries=0)
    submit = SubmitField("Save")

    @classmethod
    def from_resume(cls, raw_data: dict[str, Any]) -> "ResumeEditForm":
        """Populate a form from stored ``Resume.raw_data`` (GET requests)."""
        return cls(data=ResumeData.model_validate(raw_data).model_dump())

    def blank_entry(self, name: str) -> Form:
        """Empty subform for a list section, indexed ``__i__`` for JS cloning."""
        sub_form_class = getattr(self, name).unbound_field.args[0]
        return sub_form_class(prefix=f"{name}-__i__-")

    def to_resume_data(self) -> ResumeData:
        """Build a validated ``ResumeData``; blank strings become ``None``."""
        data = {k: v for k, v in self.data.items() if k not in ("csrf_token", "submit")}
        return ResumeData.model_validate(_blank_to_none(data))


def _blank_to_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _blank_to_none(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_blank_to_none(v) for v in value]
    if isinstance(value, str) and not value.strip():
        return None
    return value
