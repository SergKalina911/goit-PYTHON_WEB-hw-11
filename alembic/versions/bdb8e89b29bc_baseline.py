"""baseline

Revision ID: bdb8e89b29bc
Revises: d1f4ea00e81b
Create Date: 2026-05-31 12:58:33.133129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdb8e89b29bc'
down_revision: Union[str, Sequence[str], None] = 'd1f4ea00e81b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
