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
)
from flask_login import login_required
from werkzeug.utils import secure_filename

from app.ai.resume_parser import parse_resume_text
from app.extensions import dbase
from app.forms.resume_form import ResumeForm
from app.models.resume import Resume
from app.models.resume_schema import ResumeData
from app.utils.file_parser import extract_text


bp = Blueprint("resume", __name__, url_prefix="/resume")


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix in ALLOWED_EXTENSIONS


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
                filename=filename,
                raw_data=parsed_resume.model_dump(),
            )
            dbase.session.add(new_resume)
            dbase.session.commit()
            return redirect(url_for("resume.index", resume_id=new_resume.id))
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
    return render_template("pages/resume.html", resume=resume_data)
