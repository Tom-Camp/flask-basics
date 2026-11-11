from collections.abc import Iterable
from datetime import datetime

from lcat_calc.loader import default_index
from lcat_calc.models import (
    EducationLevel,
    Job,
    JobTerm,
    LcatDefinition,
    LcatIndex,
    WorkCategory,
)


def highest_education(levels: Iterable[EducationLevel | None]) -> EducationLevel | None:
    return max((lvl for lvl in levels if lvl), key=lambda lvl: lvl.rank, default=None)


def get_experience_days(cat: WorkCategory, now: datetime | None = None) -> int:
    if not cat.start_date:
        raise ValueError("No start date for category")
    end = cat.end_date or now or datetime.now()
    return (end - cat.start_date).days


def get_additional_education_years(
    lcat_education: EducationLevel, user_education: EducationLevel | None
) -> int:
    """Years of extra experience needed to offset a degree below the LCAT requirement (2 years per level)."""
    user_rank = user_education.rank if user_education else 0
    return max(lcat_education.rank - user_rank, 0) * 2


def get_category_terms(
    jobs: list[Job], now: datetime | None = None
) -> dict[str, dict[str, JobTerm]]:
    """
    Total the days worked per practice area and category, with the jobs that account for them.
    Categories without a start date are skipped.
    :return: {practice_area: {category: JobTerm}}
    """
    terms: dict[str, dict[str, JobTerm]] = {}
    for job in jobs:
        for cat in job.categories:
            if not cat.start_date:
                continue
            job_term = terms.setdefault(cat.practice_area, {}).setdefault(
                cat.category, JobTerm(term=0)
            )
            job_term.term += get_experience_days(cat, now)
            start = cat.start_date.strftime("%Y-%m-%d")
            end = cat.end_date.strftime("%Y-%m-%d") if cat.end_date else "current"
            job_term.jobs.append(
                f"{job.position} at {job.employer} from {start} to {end}"
            )
    return terms


def calculate_lcats(
    terms: dict[str, dict[str, JobTerm]],
    education: EducationLevel | None = None,
    index: LcatIndex | None = None,
) -> dict[str, list[str]]:
    """
    Find every LCAT the candidate qualifies for. An LCAT matches when the longest term in any one of its
    categories meets the LCAT minimum years plus any years needed to offset a lower education level.
    The longest single category is used rather than a sum, since one job can carry several categories.
    :return: {lcat name: jobs that support it}
    """
    index = index or default_index()
    candidates: dict[str, tuple[LcatDefinition, list[JobTerm]]] = {}
    for practice_area, categories in terms.items():
        for category, job_term in categories.items():
            for lcat in index.for_category(practice_area, category):
                candidates.setdefault(lcat.name, (lcat, []))[1].append(job_term)

    assigned: dict[str, list[str]] = {}
    for name, (lcat, matched) in candidates.items():
        required_years = lcat.min_years + get_additional_education_years(
            lcat.education, education
        )
        if max(t.term for t in matched) / 365 >= required_years:
            assigned[name] = list(dict.fromkeys(job for t in matched for job in t.jobs))
    return assigned


def derive_lcats(
    jobs: list[Job],
    education: EducationLevel | None = None,
    index: LcatIndex | None = None,
    now: datetime | None = None,
) -> dict[str, list[str]]:
    """Determine which LCATs a candidate qualifies for, given their jobs and highest education level."""
    return calculate_lcats(get_category_terms(jobs, now), education, index)
