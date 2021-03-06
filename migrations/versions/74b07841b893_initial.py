"""initial

Revision ID: 74b07841b893
Revises: 
Create Date: 2019-06-07 12:52:02.776374

"""

# revision identifiers, used by Alembic.
revision = '74b07841b893'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # ### commands auto generated by Alembic ###
    op.create_table('endpoints',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('path', sa.String(), nullable=True),
                    sa.Column('service', sa.String(), nullable=True),
                    sa.Column('methods', sa.ARRAY(sa.String()), nullable=True),
                    sa.Column('deprecated', sa.Boolean(), server_default=sa.text('false'), nullable=True),
                    sa.Column('locked', sa.Boolean(), server_default=sa.text('true'), nullable=True),
                    sa.Column('new_service', sa.String(), nullable=True),
                    sa.Column('toggle', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_endpoints_path'), 'endpoints', ['path'], unique=True)
    op.create_index(op.f('ix_endpoints_service'), 'endpoints', ['service'], unique=False)
    op.create_table('services',
                    sa.Column('name', sa.String(length=40), nullable=False),
                    sa.Column('protocols', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.Column('squad', sa.String(), nullable=True),
                    sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
                    sa.PrimaryKeyConstraint('name'),
                    sa.UniqueConstraint('name')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic ###
    op.drop_table('services')
    op.drop_index(op.f('ix_endpoints_service'), table_name='endpoints')
    op.drop_index(op.f('ix_endpoints_path'), table_name='endpoints')
    op.drop_table('endpoints')
    # ### end Alembic commands ###
