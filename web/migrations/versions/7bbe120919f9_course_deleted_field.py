"""course deleted field

Revision ID: 7bbe120919f9
Revises: 7efc2b04bc58
Create Date: 2020-08-17 00:34:36.998007

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7bbe120919f9'
down_revision = '7efc2b04bc58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('deleted', sa.Boolean(), nullable=False))
    op.add_column('courses', sa.Column('lms_id', sa.Integer(), nullable=False))
    op.alter_column('courses', 'name',
               existing_type=mysql.VARCHAR(length=140),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('courses', 'name',
               existing_type=mysql.VARCHAR(length=140),
               nullable=True)
    op.drop_column('courses', 'lms_id')
    op.drop_column('courses', 'deleted')
    # ### end Alembic commands ###
