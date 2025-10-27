"""
Initial database migration

Revision ID: 001_init
Create Date: 2025-10-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables"""
    # Tables will be created automatically by SQLAlchemy
    # This is a placeholder for future migrations
    pass


def downgrade() -> None:
    """Drop all tables"""
    pass
