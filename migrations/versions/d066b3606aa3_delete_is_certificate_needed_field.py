"""delete is_certificate_needed field

Revision ID: d066b3606aa3
Revises: 70c178f138d1
Create Date: 2020-08-25 19:40:35.950299

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd066b3606aa3'
down_revision = '70c178f138d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('courses', 'is_certificate_needed')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('is_certificate_needed', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    # ### end Alembic commands ###