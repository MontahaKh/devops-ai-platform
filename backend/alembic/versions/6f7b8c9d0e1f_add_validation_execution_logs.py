"""Add validation execution logs.

Revision ID: 6f7b8c9d0e1f
Revises: 49aa85f512c9
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6f7b8c9d0e1f"
down_revision: Union[str, Sequence[str], None] = "49aa85f512c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("validations", sa.Column("stdout", sa.Text(), nullable=True))
    op.add_column("validations", sa.Column("stderr", sa.Text(), nullable=True))
    op.add_column("validations", sa.Column("command", sa.String(length=1000), nullable=True))
    op.add_column("validations", sa.Column("exit_code", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("validations", "exit_code")
    op.drop_column("validations", "command")
    op.drop_column("validations", "stderr")
    op.drop_column("validations", "stdout")