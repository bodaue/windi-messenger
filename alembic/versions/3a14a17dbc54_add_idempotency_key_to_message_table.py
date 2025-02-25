"""Add idempotency key to Message table

Revision ID: 3a14a17dbc54
Revises: a86386916029
Create Date: 2025-02-25 21:26:55.861198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a14a17dbc54'
down_revision: Union[str, None] = 'a86386916029'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('idempotency_key', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'idempotency_key')
    # ### end Alembic commands ###
