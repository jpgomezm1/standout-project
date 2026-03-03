"""Add reservations table.

Revision ID: a1b2c3d4e5f6
Revises: 873715556cfa
Create Date: 2026-02-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "873715556cfa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "property_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("guest_name", sa.String(255), nullable=False),
        sa.Column("check_in", sa.Date(), nullable=False),
        sa.Column("check_out", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="confirmed",
        ),
        sa.Column("num_guests", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["property_id"],
            ["properties.id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "check_out > check_in",
            name="ck_reservations_checkout_after_checkin",
        ),
        sa.CheckConstraint(
            "status IN ('confirmed', 'in_progress', 'completed', 'cancelled')",
            name="ck_reservations_status",
        ),
        sa.CheckConstraint(
            "channel IN ('airbnb', 'booking', 'direct', 'other')",
            name="ck_reservations_channel",
        ),
    )

    op.create_index(
        "ix_reservations_property_id",
        "reservations",
        ["property_id"],
    )
    op.create_index(
        "ix_reservations_property_dates",
        "reservations",
        ["property_id", "check_in", "check_out"],
    )


def downgrade() -> None:
    op.drop_index("ix_reservations_property_dates", table_name="reservations")
    op.drop_index("ix_reservations_property_id", table_name="reservations")
    op.drop_table("reservations")
