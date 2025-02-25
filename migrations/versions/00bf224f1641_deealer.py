"""deealer

Revision ID: 00bf224f1641
Revises: d1c4c4472d70
Create Date: 2025-02-17 15:55:49.963629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00bf224f1641'
down_revision = 'd1c4c4472d70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('article',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('dealer',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('price',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('restaurant',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.create_unique_constraint(None, ['name'])
        batch_op.create_foreign_key(None, 'dealers', ['dealer'], ['name'])

    with op.batch_alter_table('dealers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('adres', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('e_mail', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.Integer(), nullable=True))
        batch_op.create_unique_constraint(None, ['e_mail'])
        batch_op.create_unique_constraint(None, ['phone'])
        batch_op.create_unique_constraint(None, ['adres'])
        batch_op.drop_column('category')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('dealers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('phone')
        batch_op.drop_column('e_mail')
        batch_op.drop_column('adres')

    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('restaurant',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('price',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
        batch_op.alter_column('dealer',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('article',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(),
               nullable=False)

    # ### end Alembic commands ###
