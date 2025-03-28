"""orders1.13

Revision ID: 98cb89b42967
Revises: 373db9f2d258
Create Date: 2025-03-03 02:25:29.941604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98cb89b42967'
down_revision = '373db9f2d258'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dealer_name', sa.String(), nullable=True))
        batch_op.drop_constraint('articles_dealer_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'dealers', ['dealer_name'], ['name'])
        batch_op.drop_column('dealer_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dealer_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('articles_dealer_id_fkey', 'dealers', ['dealer_id'], ['id'])
        batch_op.drop_column('dealer_name')

    # ### end Alembic commands ###
