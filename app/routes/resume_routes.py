"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    abort,
)
from flask_login import login_required, current_user
from pydantic import ValidationError
from werkzeug.utils import secure_filename

from app.ai.resume_parser import parse_resume_text
from app.extensions import dbase
from app.forms.resume_edit_form import ResumeEditForm
from app.forms.resume_form import ResumeForm
from app.models.resume import Resume
from app.models.resume_schema import ResumeData
from app.utils.file_parser import extract_text
from app.utils.helpers import BASE_DIR, load_file

CATEGORIES_FILE = BASE_DIR / "app" / "utils" / "categories.yaml"


bp = Blueprint("resume", __name__, url_prefix="/resume")


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix in ALLOWED_EXTENSIONS


def _get_owned_resume(resume_id: int) -> Resume:
    resume_data = dbase.session.get(Resume, resume_id)
    if not resume_data or resume_data.user_id != current_user.id:
        abort(404, "Resume not found")
    return resume_data


def _render_edit(form: ResumeEditForm, resume_id: int):
    return render_template(
        "pages/resume_edit.html",
        form=form,
        resume_id=resume_id,
        job_categories=load_file(CATEGORIES_FILE) or {},
    )


@bp.post("/upload")
@login_required
def process_resume():
    form = ResumeForm()

    if form.validate_on_submit():
        if "resume_file" not in request.files:
            flash("No file in request.", "error")
            return redirect(request.url)

        file = form.resume_file.data

        if not file.filename:
            flash("No selected file", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file type", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file.save(current_app.config["UPLOAD_FOLDER"] / filename)
        file.seek(0)
        read_file = file.read()
        file_text = extract_text(filename=filename, data=read_file)
        parsed_resume: ResumeData | str = current_app.ensure_sync(parse_resume_text)(
            file_text
        )
        if isinstance(parsed_resume, ResumeData):
            new_resume = Resume(
                user_id=current_user.id,
                filename=filename,
                raw_data=parsed_resume.model_dump(),
            )
            dbase.session.add(new_resume)
            dbase.session.commit()
            return redirect(url_for("resume.resume", resume_id=new_resume.id))
        else:
            flash(parsed_resume, "error")
    return redirect(url_for("resume.upload_resume"))


@bp.get("/upload")
@login_required
def upload_resume():
    form = ResumeForm()
    return render_template("pages/upload.html", form=form)


@bp.route("/<resume_id>")
@login_required
def resume(resume_id: int):
    resume_data = dbase.session.query(Resume).filter(Resume.id == resume_id).first()
    if not resume_data:
        abort(404, "Resume not found")
    no_categories: list[str] = []
    for experience in resume_data.raw_data.get("work", []):
        if not experience.get("categories", []):
            no_categories.append(
                f"{experience.get('position', '')} at {experience.get('employer_name', 'UNKNOWN')}"
            )
    if no_categories:
        flash(
            "Categories are required in order to calculate the LCATS."
            f"Categories missing for:\n\n {'\n'.join(no_categories)}. ",
            "warning",
        )
    return render_template(
        "pages/resume.html", rid=resume_id, resume=resume_data.raw_data
    )


@bp.get("/<int:resume_id>/edit")
@login_required
def resume_edit(resume_id: int):
    resume_data = _get_owned_resume(resume_id)
    for experience in resume_data.raw_data.get("work", []):
        if not experience.get("categories", []):
            flash(
                f"No categories for {experience.get('position')} at {experience.get('employer_name')}",
                "warning",
            )

    form = ResumeEditForm.from_resume(resume_data.raw_data)
    return _render_edit(form, resume_id)


@bp.post("/<int:resume_id>/edit")
@login_required
def resume_edit_process(resume_id: int):
    resume_data = _get_owned_resume(resume_id)
    form = ResumeEditForm()
    if form.validate_on_submit():
        try:
            resume_data.raw_data = form.to_resume_data().model_dump()
        except ValidationError:
            flash("Some entries are incomplete (e.g. job categories).", "error")
        else:
            dbase.session.commit()
            flash("Resume updated.", "success")
            return redirect(url_for("resume.resume", resume_id=resume_id))
    return _render_edit(form, resume_id)
