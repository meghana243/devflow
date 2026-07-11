"""changed read

Revision ID: 5cfbcad3b3e0
Revises: b26e6fbb7fde
Create Date: 2026-07-11 16:03:50.306696

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cfbcad3b3e0'
down_revision: Union[str, Sequence[str], None] = 'b26e6fbb7fde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
