"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

from flask import (
    Blueprint,
    render_template,
)
from flask_login import login_required, current_user
from app.extensions import dbase
from app.models.resume import Resume
from app.services.lcat_service import get_catalogs


bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/")
@login_required
def user_page():
    resume_data = dbase.session.execute(
        dbase.select(Resume).filter_by(user_id=current_user.id)
    ).scalar_one_or_none()

    needs_categories: bool = False
    if resume_data:
        for work in resume_data.raw_data.get("work", []):
            if not work.get("categories", []):
                needs_categories = True
    return render_template(
        "pages/user_dashboard.html",
        user=current_user,
        needs_categories=needs_categories,
        lcat_results=current_user.lcat_results or {},
        catalogs=get_catalogs().names(),
    )
