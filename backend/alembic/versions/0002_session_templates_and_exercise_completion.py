"""add session template links and exercise completion flag

Revision ID: 0002_session_templates
Revises: 0001_init_schema
Create Date: 2026-02-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0002_session_templates"
down_revision: Union[str, None] = "0001_init_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "session_template_links",
        sa.Column(
            "session_id",
            sa.Integer(),
            sa.ForeignKey("workout_sessions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "template_id",
            sa.Integer(),
            sa.ForeignKey("workout_templates.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO session_template_links (session_id, template_id)
            SELECT id, template_id
            FROM workout_sessions
            WHERE template_id IS NOT NULL
            """
        )
    )

    op.add_column(
        "session_exercises",
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("session_exercises", "is_completed", server_default=None)


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE workout_sessions ws
            SET template_id = st.min_template_id
            FROM (
                SELECT session_id, MIN(template_id) AS min_template_id
                FROM session_template_links
                GROUP BY session_id
            ) st
            WHERE ws.id = st.session_id
            """
        )
    )

    op.drop_column("session_exercises", "is_completed")
    op.drop_table("session_template_links")
