"""Убрал уникальность полей

Revision ID: 133e55a5bee5
Revises: ad39d7ea81a7
Create Date: 2020-09-04 23:49:30.451128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '133e55a5bee5'
down_revision = 'ad39d7ea81a7'
branch_labels = None
depends_on = None


def upgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_index('email', table_name='students')
    # op.drop_index('lms_email', table_name='students')
    # ### end Alembic commands ###


def downgrade():
    pass
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_index('lms_email', 'students', ['lms_email'], unique=True)
    # op.create_index('email', 'students', ['email'], unique=True)
    # ### end Alembic commands ###
