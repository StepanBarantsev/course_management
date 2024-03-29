"""Добавил модель дз

Revision ID: 4c4b76fc7d44
Revises: 448ccbb529c1
Create Date: 2021-02-02 19:22:27.095951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c4b76fc7d44'
down_revision = '448ccbb529c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('homeworks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lms_id', sa.Integer(), nullable=True),
    sa.Column('short_name', sa.String(length=100), nullable=True),
    sa.Column('answer_link', sa.String(length=100), nullable=True),
    sa.Column('deleted', sa.Boolean(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('courses', sa.Column('number_of_homeworks', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('courses', 'number_of_homeworks')
    op.drop_table('homeworks')
    # ### end Alembic commands ###
