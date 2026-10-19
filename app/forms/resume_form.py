"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

from flask_wtf import FlaskForm
from wtforms.fields import FileField, SubmitField
from wtforms.validators import DataRequired


class ResumeForm(FlaskForm):
    resume_file = FileField(
        validators=[DataRequired()],
        render_kw={
            "class": "shadow appearance-none border border-red-500 rounded w-full py-2 px-3 text-gray-700 "
            "mb-3 leading-tight focus:outline-none focus:shadow-outline"
        },
    )
    submit = SubmitField(
        "Submit",
        render_kw={
            "class": "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none "
            "focus:shadow-outline",
        },
    )
