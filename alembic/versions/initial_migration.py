"""Initial migration

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2025-04-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create portfolios table
    op.create_table('portfolios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('risk_level', sa.Integer(), nullable=True),
        sa.Column('initial_investment', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolios_id'), 'portfolios', ['id'], unique=False)
    op.create_index(op.f('ix_portfolios_name'), 'portfolios', ['name'], unique=False)

    # Create allocations table
    op.create_table('allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=True),
        sa.Column('asset_type', sa.String(), nullable=True),
        sa.Column('asset_name', sa.String(), nullable=True),
        sa.Column('ticker', sa.String(), nullable=True),
        sa.Column('percentage', sa.Float(), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_allocations_id'), 'allocations', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_allocations_id'), table_name='allocations')
    op.drop_table('allocations')
    op.drop_index(op.f('ix_portfolios_name'), table_name='portfolios')
    op.drop_index(op.f('ix_portfolios_id'), table_name='portfolios')
    op.drop_table('portfolios')