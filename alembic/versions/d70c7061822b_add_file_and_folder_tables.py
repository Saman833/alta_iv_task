"""add file and folder tables

Revision ID: d70c7061822b
Revises: b66bac4a05cd
Create Date: 2025-07-10 04:05:52.571488

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd70c7061822b'
down_revision: Union[str, Sequence[str], None] = 'b66bac4a05cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create table for storing table metadata
    op.create_table('table',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('table_name', sa.String(length=255), nullable=False),
        sa.Column('folder_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('table_description', sa.Text(), nullable=True),
        sa.Column('table_created_at', sa.DateTime(), nullable=True),
        sa.Column('table_updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create folder table
    op.create_table('folder',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('folder_name', sa.String(length=255), nullable=False),
        sa.Column('detail_summary', sa.Text(), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('folder_created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create file table
    op.create_table('file',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('detail_summary', sa.Text(), nullable=True),
        sa.Column('folder_id', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('file_created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key constraints
    op.create_foreign_key('fk_file_folder', 'file', 'folder', ['folder_id'], ['id'])
    op.create_foreign_key('fk_table_folder', 'table', 'folder', ['folder_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraints first
    op.drop_constraint('fk_table_folder', 'table', type_='foreignkey')
    op.drop_constraint('fk_file_folder', 'file', type_='foreignkey')
    
    # Drop tables
    op.drop_table('file')
    op.drop_table('folder')
    op.drop_table('table')
