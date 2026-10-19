"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

import os
import logging

from datetime import datetime

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.exceptions import ModelHTTPError

from app.models.resume_schema import ResumeData

log = logging.getLogger(__name__)

_agent = Agent(
    GoogleModel(os.environ.get("GEMINI_AGENT", "gemini-3.1-flash-lite-preview")),
    output_type=ResumeData,
    system_prompt=(
        "You are a resume parser. Extract all available information from the provided "
        "resume text into the structured output format. Use YYYY-MM-DD or YYYY-MM for "
        "dates where possible. "
        "For work experience, always extract BOTH start_date AND end_date when a date "
        "range is present (e.g. '2013 – 2015' means start_date='2013' end_date='2015'). "
        "Only set end_date to null for the current/ongoing job. "
        "Omit fields that are not present in the resume rather than guessing."
    ),
)


def _infer_end_dates(data: ResumeData) -> ResumeData:
    """Fill in missing end dates for past work items using the next job's start date.

    For a typical sequential career, if a past job lacks an end date the most
    reliable estimate is the start date of the job that followed it.  The most
    recent entry (likely the current role) is left unchanged.

    Jobs with an existing end_date are never overwritten.
    """
    work = data.work
    if len(work) < 2:
        return data

    # Build a list sorted newest-first by start_date so we can look ahead.
    indexed = sorted(
        enumerate(work),
        key=lambda x: x[1].start_date or datetime.min,
        reverse=True,
    )

    # For each job except the most recent one: if end_date is missing and the
    # next-newer job has a start_date, use that start_date as the end_date.
    inferred = 0
    for rank, (orig_idx, job) in enumerate(indexed):
        if rank == 0:
            continue  # most recent job — leave end_date as-is
        if job.end_date is not None:
            continue  # already has an end date
        newer_job = indexed[rank - 1][1]
        if newer_job.start_date is not None:
            data.work[orig_idx].end_date = newer_job.start_date
            inferred += 1

    if inferred:
        log.info("resume_parse.end_dates_inferred")
    return data


async def parse_resume_text(text: str) -> ResumeData | str:
    """Extract structured resume data from plain text using Gemini.

    Args:
        text: Plain text extracted from the uploaded resume file.

    Returns:
        A validated ResumeData instance with end dates inferred where missing or an error message.
    """
    log.info("resume_parse.start")
    try:
        result = await _agent.run(f"Parse this resume:\n\n{text}")
        data = _infer_end_dates(result.output)
        log.info("resume_parse.complete")
        return data
    except ModelHTTPError as e:
        message = e.message
        log.error(message)
        return message
