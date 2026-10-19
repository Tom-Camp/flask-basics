"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, String, Text, event, inspect
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.extensions import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.users import User


class Resume(BaseModel):
    __tablename__ = "resumes"
    tracked_fields: ClassVar[tuple[str, ...]] = ("filename", "raw_data")

    filename: Mapped[str] = mapped_column(String(64), active_history=True)
    raw_data: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict,
        active_history=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["User"] = relationship(back_populates="resumes")
    revisions: Mapped[list["ResumeRevisions"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="ResumeRevisions.id",
    )

    def __repr__(self) -> str:
        return f"<Resume {self.id} {self.filename!r}>"


class ResumeRevisions(Base):
    __tablename__ = "resume_revisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), index=True)
    field: Mapped[str] = mapped_column(String(64))
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    resume: Mapped["Resume"] = relationship(back_populates="revisions")


@event.listens_for(Session, "before_flush")
def record_revisions(session: Session, flush_context, instances) -> None:
    for obj in list(session.dirty):
        if not isinstance(obj, Resume):
            continue
        state = inspect(obj)
        for name in obj.tracked_fields:
            hist = state.attrs[name].history
            if not hist.has_changes():
                continue
            obj.revisions.append(
                ResumeRevisions(
                    field=name,
                    old_value=hist.deleted[0] if hist.deleted else None,
                    new_value=hist.added[0] if hist.added else None,
                )
            )
