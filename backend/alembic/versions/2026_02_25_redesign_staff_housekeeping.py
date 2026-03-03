"""Redesign staff/housekeeping: add housekeeping_assignments table, housekeepers_needed column, clean housekeeper assignments.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add housekeepers_needed column to properties
    op.add_column(
        "properties",
        sa.Column("housekeepers_needed", sa.Integer(), nullable=False, server_default="1"),
    )

    # 2. Create housekeeping_assignments table
    op.create_table(
        "housekeeping_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "reservation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reservations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "staff_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("staff_members.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="scheduled",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled')",
            name="ck_housekeeping_assignments_status",
        ),
        sa.UniqueConstraint(
            "reservation_id", "staff_id", "scheduled_date",
            name="uq_housekeeping_assignment",
        ),
    )

    op.create_index(
        "ix_housekeeping_assignments_reservation_id",
        "housekeeping_assignments",
        ["reservation_id"],
    )
    op.create_index(
        "ix_housekeeping_assignments_staff_date",
        "housekeeping_assignments",
        ["staff_id", "scheduled_date"],
    )

    # 3. Remove housekeeper rows from property_staff_assignments
    op.execute(
        """
        DELETE FROM property_staff_assignments
        WHERE staff_id IN (
            SELECT id FROM staff_members WHERE role = 'housekeeper'
        )
        """
    )


def downgrade() -> None:
    op.drop_table("housekeeping_assignments")
    op.drop_column("properties", "housekeepers_needed")
