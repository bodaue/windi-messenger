"""Update MessageReadState

Revision ID: dff01af2f411
Revises: 86104c8c65dd
Create Date: 2025-02-22 11:42:38.758109

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dff01af2f411"
down_revision: str | None = "86104c8c65dd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("message_read_states", "is_read")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "message_read_states",
        sa.Column("is_read", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    # ### end Alembic commands ###
