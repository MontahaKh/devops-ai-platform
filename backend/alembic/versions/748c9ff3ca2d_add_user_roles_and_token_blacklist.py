"""Add user roles and token blacklist

Revision ID: 748c9ff3ca2d
Revises: 327301a548f5
Create Date: 2026-08-31 18:45:58.659003
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '748c9ff3ca2d'
down_revision: Union[str, Sequence[str], None] = '327301a548f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add role column to users table
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=False, server_default='user'))
    
    # Create token_blacklist table
    op.create_table(
        'token_blacklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(length=500), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', postgresql.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('token_blacklist_pkey')),
        sa.UniqueConstraint('jti', name=op.f('token_blacklist_jti_key'))
    )


def downgrade() -> None:
    # Drop token_blacklist table
    op.drop_table('token_blacklist')
    
    # Remove role column from users table
    op.drop_column('users', 'role')
