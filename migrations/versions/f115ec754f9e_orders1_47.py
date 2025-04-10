"""orders1.47

Revision ID: f115ec754f9e
Revises: 1eb828224bc8
Create Date: 2025-03-22 20:42:42.364018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f115ec754f9e'
down_revision = '1eb828224bc8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_goods', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dealer_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'dealers', ['dealer_id'], ['id'])
        batch_op.drop_column('article_multiplicity')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_goods', schema=None) as batch_op:
        batch_op.add_column(sa.Column('article_multiplicity', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('dealer_id')

    # ### end Alembic commands ###
