"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

import lcat_calc
from flask import current_app
from lcat_calc import CatalogRegistry, EducationLevel, Job, WorkCategory

from app.models.resume_schema import ResumeData


def get_catalogs() -> CatalogRegistry:
    return current_app.extensions["lcat_catalogs"]


def derive_lcats(
    resume: ResumeData, catalog: str = lcat_calc.DEFAULT_CATALOG
) -> dict[str, list[str]]:
    """
    Map a resume onto the lcat_calc input types and return {lcat name: supporting jobs}.
    :raises KeyError: if the catalog does not exist
    """
    index = get_catalogs().index(catalog)
    jobs = [
        Job(
            position=work.position,
            employer=work.employer_name,
            categories=[
                WorkCategory(
                    practice_area=cat.practice_area,
                    category=cat.category,
                    start_date=cat.start_date,
                    end_date=cat.end_date,
                )
                for cat in work.categories
            ],
        )
        for work in resume.work
    ]
    education = lcat_calc.highest_education(
        EducationLevel(edu.degree_type.value) if edu.degree_type else None
        for edu in resume.education
    )
    return lcat_calc.derive_lcats(jobs, education, index=index)
