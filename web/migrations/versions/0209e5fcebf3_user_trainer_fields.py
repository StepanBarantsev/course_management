"""user trainer fields

Revision ID: 0209e5fcebf3
Revises: 0c726da64367
Create Date: 2020-08-19 01:52:44.059412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0209e5fcebf3'
down_revision = '0c726da64367'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('lms_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('telegram_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'telegram_id')
    op.drop_column('users', 'lms_id')
    # ### end Alembic commands ###