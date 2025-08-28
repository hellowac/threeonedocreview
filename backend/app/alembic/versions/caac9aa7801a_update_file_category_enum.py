# type: ignore

"""update enum values for file_category in document table

Revision ID: caac9aa7801a
Revises: eef8805e44ed
Create Date: 2025-08-28 17:28:45.158619

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
import app


# revision identifiers, used by Alembic.
revision = 'caac9aa7801a'
down_revision = 'eef8805e44ed'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "document",
        "file_category",
        existing_type=sa.Enum(
            "THREESTEP",
            "METTING",
            "FEASIBIBITY",
            "SURVEY",
            "OTHER",
            name="filecategory",
        ),
        type_=sa.Enum(
            "THREESTEP",
            "METTING",
            "FEASIBIBITY",
            "SURVEY",
            "OTHER",
            "SAFETOOL",
            "BUILDTOOL",
            name="filecategory",
        ),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "document",
        "file_category",
        existing_type=sa.Enum(
            "THREESTEP",
            "METTING",
            "FEASIBIBITY",
            "SURVEY",
            "OTHER",
            "SAFETOOL",
            "BUILDTOOL",
            name="filecategory",
        ),
        type_=sa.Enum(
            "THREESTEP",
            "METTING",
            "FEASIBIBITY",
            "SURVEY",
            "OTHER",
            name="filecategory",
        ),
        existing_nullable=False,
    )
