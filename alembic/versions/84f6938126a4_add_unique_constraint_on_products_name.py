"""add unique constraint on products.name

Revision ID: 84f6938126a4
Revises: b511262800b6
Create Date: 2025-08-11 14:47:36.818615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84f6938126a4'
down_revision: Union[str, Sequence[str], None] = 'b511262800b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_products_name", "products", ["name"])


def downgrade() -> None:
    op.drop_constraint("uq_products_name", "products", type_="unique")
