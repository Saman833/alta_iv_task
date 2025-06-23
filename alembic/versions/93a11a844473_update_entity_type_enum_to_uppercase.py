"""Update entity type enum to uppercase

Revision ID: 93a11a844473
Revises: 5db0b795de02
Create Date: 2025-06-23 10:38:14.424907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93a11a844473'
down_revision: Union[str, Sequence[str], None] = '5db0b795de02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update entity_type enum values from lowercase to uppercase
    with op.batch_alter_table('entity', recreate='always') as batch_op:
        batch_op.alter_column('entity_type',
            existing_type=sa.Enum('email', 'contact', 'date', 'keyword', name='entitytype'),
            type_=sa.Enum('EMAIL', 'CONTACT', 'DATE', 'KEYWORD', name='entitytype'),
            existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert entity_type enum values back to lowercase
    with op.batch_alter_table('entity', recreate='always') as batch_op:
        batch_op.alter_column('entity_type',
            existing_type=sa.Enum('EMAIL', 'CONTACT', 'DATE', 'KEYWORD', name='entitytype'),
            type_=sa.Enum('email', 'contact', 'date', 'keyword', name='entitytype'),
            existing_nullable=False) 