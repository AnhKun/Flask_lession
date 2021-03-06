"""empty message

Revision ID: 0750bf733b37
Revises: ba45d5fc0760
Create Date: 2021-12-06 12:54:58.655541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0750bf733b37'
down_revision = 'ba45d5fc0760'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follower',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followee_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followee_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('follower')
    # ### end Alembic commands ###
