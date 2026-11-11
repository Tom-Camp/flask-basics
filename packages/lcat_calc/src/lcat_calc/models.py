from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel, Field


class EducationLevel(StrEnum):
    # Declaration order is the rank order, lowest to highest.
    OTHER = auto()
    ASSOCIATE = auto()
    BACHELORS = auto()
    MASTERS = auto()
    DOCTORATE = auto()

    @property
    def rank(self) -> int:
        return list(EducationLevel).index(self)


class WorkCategory(BaseModel):
    """A category a candidate worked in during one job. A missing end_date means the job is current."""

    practice_area: str
    category: str
    start_date: datetime | None = None
    end_date: datetime | None = None


class Job(BaseModel):
    position: str | None = None
    employer: str | None = None
    categories: list[WorkCategory] = Field(default_factory=list)


class JobTerm(BaseModel):
    term: int
    jobs: list[str] = Field(default_factory=list)


class CategoryRef(BaseModel, frozen=True):
    practice_area: str
    category: str


class LcatDefinition(BaseModel):
    name: str
    education: EducationLevel
    min_years: int
    experience: str
    categories: list[CategoryRef]


class LcatIndex(BaseModel):
    """LCAT definitions keyed by (practice_area, category) for direct lookup."""

    by_category: dict[tuple[str, str], list[LcatDefinition]]

    def for_category(self, practice_area: str, category: str) -> list[LcatDefinition]:
        return self.by_category.get((practice_area, category), [])
