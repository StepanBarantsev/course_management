"""added is_certificate_needed field

Revision ID: 70c178f138d1
Revises: ea54b96ff65f
Create Date: 2020-08-25 19:34:54.967289

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70c178f138d1'
down_revision = 'ea54b96ff65f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('is_certificate_needed', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('courses', 'is_certificate_needed')
    # ### end Alembic commands ###
