"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

from flask import (
    Blueprint,
    render_template,
)
from flask_login import login_required, current_user


bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/")
@login_required
def user_page():
    user = current_user
    return render_template("pages/user.html", user=user)
