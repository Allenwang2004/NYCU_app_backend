"""change activity to array

Revision ID: e2414525bfcd
Revises: b4bbef6b4070
Create Date: 2025-05-25 14:28:16.478030

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'e2414525bfcd'
down_revision = 'b4bbef6b4070'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'user_profiles',
        'activity',
        existing_type=sa.Text(),
        type_=postgresql.ARRAY(sa.Text()),
        existing_nullable=True,
        postgresql_using="activity::text[]"  # 加這一行
    )


def downgrade():
    op.alter_column('user_profiles', 'activity',
        existing_type=postgresql.ARRAY(sa.Text()),
        type_=sa.Text(),
        existing_nullable=True
    )
