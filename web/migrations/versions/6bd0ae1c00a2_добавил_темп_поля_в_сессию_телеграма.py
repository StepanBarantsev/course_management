"""Добавил темп поля в сессию телеграма

Revision ID: 6bd0ae1c00a2
Revises: 638a27189f75
Create Date: 2020-09-12 21:44:35.894230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bd0ae1c00a2'
down_revision = '638a27189f75'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_index('lms_id', table_name='courses')
    op.add_column('telegram_states', sa.Column('temp_authcode', sa.String(length=100), nullable=True))
    op.add_column('telegram_states', sa.Column('temp_lms_email', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('telegram_states', 'temp_lms_email')
    op.drop_column('telegram_states', 'temp_authcode')
    # op.create_index('lms_id', 'courses', ['lms_id'], unique=True)
    # ### end Alembic commands ###
