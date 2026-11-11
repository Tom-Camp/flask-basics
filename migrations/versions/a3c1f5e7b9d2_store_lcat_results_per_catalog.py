"""Store LCAT results per catalog

Replaces the comma-joined users.lcats string with users.lcat_results, a JSON map of
catalog name to LCAT names. Existing lcats values are dropped (the feature never
produced any).

Revision ID: a3c1f5e7b9d2
Revises: d74725e627d3
Create Date: 2026-11-11 09:40:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a3c1f5e7b9d2"
down_revision = "d74725e627d3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("lcat_results", sa.JSON(), nullable=True))
        batch_op.drop_column("lcats")


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("lcats", sa.String(length=255), nullable=True))
        batch_op.drop_column("lcat_results")
