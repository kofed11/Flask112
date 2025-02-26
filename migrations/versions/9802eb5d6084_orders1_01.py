"""orders1.01

Revision ID: 9802eb5d6084
Revises: a894cf37ef02
Create Date: 2025-02-26 14:58:18.181784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9802eb5d6084'
down_revision = 'a894cf37ef02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dealer_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('orders_dealer_name_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'dealers', ['dealer_id'], ['id'])
        batch_op.drop_column('dealer_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dealer_name', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('orders_dealer_name_fkey', 'dealers', ['dealer_name'], ['name'])
        batch_op.drop_column('dealer_id')

    # ### end Alembic commands ###
