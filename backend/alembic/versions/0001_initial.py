"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-17 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("google_tokens", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "meetings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("candidate_name", sa.String(120), nullable=False),
        sa.Column("candidate_email", sa.String(255), nullable=True),
        sa.Column("position", sa.String(120), nullable=False),
        sa.Column("department", sa.String(40), nullable=False),
        sa.Column("host_id", sa.String(), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_mins", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("location_type", sa.String(20), nullable=False),
        sa.Column("location_detail", sa.String(512), nullable=True),
        sa.Column("google_event_id", sa.String(255), nullable=True),
        sa.Column("meet_link", sa.String(512), nullable=True),
        sa.Column("notes", sa.String(2048), nullable=True),
        sa.Column("participants", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(20), nullable=False, server_default="SCHEDULED"),
        sa.Column("color_tag", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["host_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("meeting_id", sa.String(), nullable=False),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("actor_id", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meeting_id"], ["meetings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("meetings")
    op.drop_table("users")
