"""add is_send column

Revision ID: f5e8068189ad
Revises: c59397104e9e
Create Date: 2024-08-25 06:52:42.151355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5e8068189ad'
down_revision: Union[str, None] = 'c59397104e9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('frame_video', sa.Column('is_send', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('frame_video', 'is_send')
    # ### end Alembic commands ###
