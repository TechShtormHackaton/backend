"""update db

Revision ID: 7cb293b1aad9
Revises: 311bde61aa05
Create Date: 2024-08-25 11:39:45.573233

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cb293b1aad9'
down_revision: Union[str, None] = '311bde61aa05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('frame_video', sa.Column('safes_state', sa.Integer(), nullable=True))
    op.drop_column('frame_video', 'empty_state')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('frame_video', sa.Column('empty_state', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('frame_video', 'safes_state')
    # ### end Alembic commands ###
