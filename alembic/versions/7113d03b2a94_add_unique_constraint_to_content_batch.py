"""add_unique_constraint_to_content_batch

Revision ID: 7113d03b2a94
Revises: 8420d94c2776
Create Date: 2025-06-23 00:41:08.347656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7113d03b2a94'
down_revision: Union[str, Sequence[str], None] = '8420d94c2776'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema using batch mode for SQLite."""
    with op.batch_alter_table('content', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_source_id_source', ['source_id', 'source'])


def downgrade() -> None:
    """Downgrade schema using batch mode for SQLite."""
    with op.batch_alter_table('content', schema=None) as batch_op:
        batch_op.drop_constraint('uq_source_id_source', type_='unique')
