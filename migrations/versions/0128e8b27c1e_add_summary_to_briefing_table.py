"""add summary to briefing table

Revision ID: 0128e8b27c1e
Revises: 1d268c5532f9
Create Date: 2020-01-31 18:07:38.221869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0128e8b27c1e'
down_revision = '1d268c5532f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('briefing', sa.Column('summary', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('briefing', 'summary')
    # ### end Alembic commands ###
