"""Add is_searchable to disease table

Revision ID: 001_add_is_searchable
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_is_searchable'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    try:
        # diseasesテーブルが存在するか確認
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        
        if 'diseases' in inspector.get_table_names():
            # カラムが存在するか確認
            columns = [col['name'] for col in inspector.get_columns('diseases')]
            if 'is_searchable' not in columns:
                op.add_column('diseases', sa.Column('is_searchable', sa.Boolean(), nullable=True))
                op.execute("UPDATE diseases SET is_searchable = TRUE WHERE is_searchable IS NULL")
                print("Added is_searchable column")
            else:
                print("is_searchable column already exists")
        else:
            print("diseases table does not exist")
    except Exception as e:
        print(f"Error during upgrade: {e}")


def downgrade() -> None:
    try:
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        
        if 'diseases' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('diseases')]
            if 'is_searchable' in columns:
                op.drop_column('diseases', 'is_searchable')
                print("Dropped is_searchable column")
        else:
            print("diseases table does not exist")
    except Exception as e:
        print(f"Error during downgrade: {e}")
