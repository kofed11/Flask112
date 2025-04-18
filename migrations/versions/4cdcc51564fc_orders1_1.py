"""orders1.1

Revision ID: 4cdcc51564fc
Revises: 3989aa69069b
Create Date: 2025-02-26 14:04:43.044639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cdcc51564fc'
down_revision = '3989aa69069b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_constraint('orders_user_username_fkey', type_='foreignkey')
        batch_op.drop_column('user_username')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_username', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('orders_user_username_fkey', 'user2', ['user_username'], ['username'])

    # ### end Alembic commands ###
