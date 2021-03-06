"""link field

Revision ID: 459756de569f
Revises: a0a38d9dc506
Create Date: 2020-08-25 23:47:55.214314

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '459756de569f'
down_revision = 'a0a38d9dc506'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('link', sa.String(length=140), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('courses', 'link')
    # ### end Alembic commands ###
