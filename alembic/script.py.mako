"""${message}

ID de révision: ${up_revision}
Révise: ${down_revision | comma,n}
Date de création: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Identificateurs de révision, utilisés par Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Mettre à jour le schéma."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Annuler les modifications du schéma."""
    ${downgrades if downgrades else "pass"}
