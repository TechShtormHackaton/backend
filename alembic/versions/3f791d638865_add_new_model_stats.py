"""add new model STATS

Revision ID: 3f791d638865
Revises: 5349ebc833e5
Create Date: 2024-08-24 13:57:12.455106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f791d638865'
down_revision: Union[str, None] = '5349ebc833e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('video_id', sa.Integer(), nullable=True),
    sa.Column('total_states', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['video_id'], ['video_path.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('frame_video', sa.Column('power_state', sa.Integer(), nullable=True))
    op.add_column('frame_video', sa.Column('throws', sa.Integer(), nullable=True))
    op.add_column('frame_video', sa.Column('empty_state', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('frame_video', 'empty_state')
    op.drop_column('frame_video', 'throws')
    op.drop_column('frame_video', 'power_state')
    op.drop_table('stats')
    # ### end Alembic commands ###
