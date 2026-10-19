"""Pydantic models for the jsonresume schema.

These are used as the Pydantic AI response type and as the data contract
throughout the application. All fields are nullable so the AI can produce
a partial result when information is absent from the source document.

Schema reference: https://github.com/jsonresume/resume-schema/blob/master/schema.json
"""

from datetime import datetime
from typing import Annotated

from dateutil import parser as _dateutil
from pydantic import BaseModel, BeforeValidator, PlainSerializer

_PRESENT_WORDS = {"present", "current", "now", "ongoing", ""}


def _parse_flexible_date(v: object) -> datetime | None:
    """Accept any date string dateutil can interpret, plus 'present' synonyms."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v
    s = str(v).strip()
    if s.lower() in _PRESENT_WORDS:
        return None
    try:
        return _dateutil.parse(s, default=datetime(1900, 1, 1))
    except (ValueError, OverflowError):
        return None


FlexDate = Annotated[
    datetime | None,
    BeforeValidator(_parse_flexible_date),
    PlainSerializer(
        lambda v: v.strftime("%Y-%m-%d") if v is not None else None,
        return_type=str | None,
    ),
]


class JobCategory(BaseModel):
    practice_area: str
    category: str
    start_date: FlexDate = None
    end_date: FlexDate = None
    is_current: bool = False


class Location(BaseModel):
    address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    country_code: str | None = None
    region: str | None = None


class Profile(BaseModel):
    network: str | None = None
    username: str | None = None
    url: str | None = None


class Basics(BaseModel):
    name: str | None = None
    label: str | None = None
    image: str | None = None
    email: str | None = None
    phone: str | None = None
    url: str | None = None
    summary: str | None = None
    location: Location | None = None
    profiles: list[Profile] = []


class WorkExperience(BaseModel):
    employer_name: str | None = None
    position: str | None = None
    url: str | None = None
    start_date: FlexDate = None
    end_date: FlexDate = None
    summary: str | None = None
    highlights: list[str] = []
    categories: list[JobCategory] = []


class VolunteerExperience(BaseModel):
    organization: str | None = None
    position: str | None = None
    url: str | None = None
    start_date: FlexDate = None
    end_date: FlexDate = None
    summary: str | None = None
    highlights: list[str] = []


class Education(BaseModel):
    institution: str | None = None
    url: str | None = None
    area: str | None = None
    degree_type: str | None = None
    start_date: FlexDate = None
    end_date: FlexDate = None
    score: str | None = None
    courses: list[str] = []


class Award(BaseModel):
    title: str | None = None
    date: FlexDate = None
    awarder: str | None = None
    summary: str | None = None


class Certificate(BaseModel):
    name: str | None = None
    date: FlexDate = None
    issuer: str | None = None
    url: str | None = None


class Publication(BaseModel):
    name: str | None = None
    publisher: str | None = None
    release_date: FlexDate = None
    url: str | None = None
    summary: str | None = None


class Skill(BaseModel):
    name: str | None = None
    level: str | None = None
    keywords: list[str] = []


class Language(BaseModel):
    language: str | None = None
    fluency: str | None = None


class Interest(BaseModel):
    name: str | None = None
    keywords: list[str] = []


class Reference(BaseModel):
    name: str | None = None
    reference: str | None = None


class Project(BaseModel):
    name: str | None = None
    description: str | None = None
    highlights: list[str] = []
    keywords: list[str] = []
    start_date: FlexDate = None
    end_date: FlexDate = None
    url: str | None = None
    roles: list[str] = []
    company: str | None = None
    job_type: str | None = None


class ResumeData(BaseModel):
    """
    Structured resume conforming to the jsonresume schema.

    Used as the Pydantic AI result type and as the application data contract.
    """

    basics: Basics | None = None
    work: list[WorkExperience] = []
    volunteer: list[VolunteerExperience] = []
    education: list[Education] = []
    awards: list[Award] = []
    certificates: list[Certificate] = []
    publications: list[Publication] = []
    skills: list[Skill] = []
    languages: list[Language] = []
    interests: list[Interest] = []
    references: list[Reference] = []
    projects: list[Project] = []
