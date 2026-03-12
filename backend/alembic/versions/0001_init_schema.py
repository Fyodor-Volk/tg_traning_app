"""init schema

Revision ID: 0001_init_schema
Revises: 
Create Date: 2026-02-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0001_init_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    op.create_table(
        "workout_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workout_templates_id", "workout_templates", ["id"])
    op.create_index("ix_workout_templates_user_id", "workout_templates", ["user_id"])

    op.create_table(
        "template_exercises",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "template_id",
            sa.Integer(),
            sa.ForeignKey("workout_templates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exercise_name", sa.String(length=255), nullable=False),
        sa.Column("sets_default", sa.Integer(), nullable=False),
        sa.Column("reps_default", sa.Integer(), nullable=False),
        sa.Column("weight_default", sa.Float(), nullable=True),
    )
    op.create_index("ix_template_exercises_id", "template_exercises", ["id"])
    op.create_index(
        "ix_template_exercises_template_id",
        "template_exercises",
        ["template_id"],
    )

    op.create_table(
        "workout_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("workout_templates.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workout_sessions_id", "workout_sessions", ["id"])
    op.create_index("ix_workout_sessions_user_id", "workout_sessions", ["user_id"])
    op.create_index("ix_workout_sessions_date", "workout_sessions", ["date"])

    op.create_table(
        "session_exercises",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Integer(),
            sa.ForeignKey("workout_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("exercise_name", sa.String(length=255), nullable=False),
        sa.Column("sets", sa.Integer(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
    )
    op.create_index("ix_session_exercises_id", "session_exercises", ["id"])
    op.create_index("ix_session_exercises_session_id", "session_exercises", ["session_id"])

    op.create_table(
        "body_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("chest", sa.Float(), nullable=True),
        sa.Column("waist", sa.Float(), nullable=True),
        sa.Column("hips", sa.Float(), nullable=True),
        sa.Column("biceps", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_body_metrics_id", "body_metrics", ["id"])
    op.create_index("ix_body_metrics_user_id", "body_metrics", ["user_id"])
    op.create_index("ix_body_metrics_date", "body_metrics", ["date"])


def downgrade() -> None:
    op.drop_index("ix_body_metrics_date", table_name="body_metrics")
    op.drop_index("ix_body_metrics_user_id", table_name="body_metrics")
    op.drop_index("ix_body_metrics_id", table_name="body_metrics")
    op.drop_table("body_metrics")

    op.drop_index("ix_session_exercises_session_id", table_name="session_exercises")
    op.drop_index("ix_session_exercises_id", table_name="session_exercises")
    op.drop_table("session_exercises")

    op.drop_index("ix_workout_sessions_date", table_name="workout_sessions")
    op.drop_index("ix_workout_sessions_user_id", table_name="workout_sessions")
    op.drop_index("ix_workout_sessions_id", table_name="workout_sessions")
    op.drop_table("workout_sessions")

    op.drop_index("ix_template_exercises_template_id", table_name="template_exercises")
    op.drop_index("ix_template_exercises_id", table_name="template_exercises")
    op.drop_table("template_exercises")

    op.drop_index("ix_workout_templates_user_id", table_name="workout_templates")
    op.drop_index("ix_workout_templates_id", table_name="workout_templates")
    op.drop_table("workout_templates")

    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")

