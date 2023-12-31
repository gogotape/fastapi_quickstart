"""Add new field to Product model

Revision ID: 5e7f540d75aa
Revises: e3eb8c3e405d
Create Date: 2023-12-10 01:57:18.919428

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5e7f540d75aa'
down_revision: Union[str, None] = 'e3eb8c3e405d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Product', sa.Column('description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Product', 'description')
    # ### end Alembic commands ###
