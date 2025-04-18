"""orders1.9

Revision ID: a894cf37ef02
Revises: 61d265cb4a89
Create Date: 2025-02-26 14:23:25.466292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a894cf37ef02'
down_revision = '61d265cb4a89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_constraint('orders_dealer_name_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'articles', ['dealer_name'], ['dealer'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('orders_dealer_name_fkey', 'dealers', ['dealer_name'], ['name'])

    # ### end Alembic commands ###
