"""remove_external_id_from_customers

Revision ID: 3c4b117deefc
Revises: 2b3a006cbbfa
Create Date: 2026-04-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c4b117deefc'
down_revision: Union[str, None] = '2b3a006cbbfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('ix_customers_external_id', table_name='customers', if_exists=True)
    op.drop_column('customers', 'external_id')


def downgrade() -> None:
    op.add_column(
        'customers',
        sa.Column('external_id', sa.String(length=100), nullable=True),
    )
    op.create_index(
        'ix_customers_external_id', 'customers', ['external_id'], unique=True
    )
