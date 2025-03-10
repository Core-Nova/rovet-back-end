"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-02-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.models.user import UserRole

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create UserRole enum type if it doesn't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_enums = inspector.get_enums()
    
    if not any(enum['name'] == 'userrole' for enum in existing_enums):
        userrole = postgresql.ENUM(UserRole, name='userrole')
        userrole.create(conn)
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', postgresql.ENUM(UserRole, name='userrole', create_type=False), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    
    # Drop table
    op.drop_table('users')
    
    # Drop enum type if it exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_enums = inspector.get_enums()
    
    if any(enum['name'] == 'userrole' for enum in existing_enums):
        userrole = postgresql.ENUM(name='userrole')
        userrole.drop(conn) 