"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

import lcat_calc
from lcat_calc import EducationLevel, Job, WorkCategory

from app.models.resume_schema import ResumeData


def derive_lcats(resume: ResumeData) -> dict[str, list[str]]:
    """Map a resume onto the lcat_calc input types and return {lcat name: supporting jobs}."""
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
    return lcat_calc.derive_lcats(jobs, education)
