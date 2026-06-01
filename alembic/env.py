from logging.config import fileConfig
import sys
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Charger les variables d'environnement depuis .env
load_dotenv()

# Ajouter le répertoire parent au sys.path pour importer les modèles
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Importer les modèles pour la génération automatique
from app.database import Base
from app.models import *  # Importer tous les modèles

# Ceci est l'objet Config Alembic, qui fournit
# l'accès aux valeurs dans le fichier .ini utilisé.
config = context.config

# Remplacer l'URL de la base de données par celle du .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Interpréter le fichier de configuration pour la journalisation Python.
# Cette ligne configure les loggers de base.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ajouter l'objet MetaData de votre modèle ici
# pour le support 'autogenerate'
target_metadata = Base.metadata

# D'autres valeurs de la configuration, définies par les besoins de env.py,
# peuvent être acquises:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Exécuter les migrations en mode 'hors ligne'.

    Cela configure le contexte avec seulement une URL
    et pas de Engine, bien qu'un Engine soit acceptable
    ici aussi. En sautant la création de l'Engine
    nous n'avons même pas besoin d'un DBAPI disponible.

    Les appels à context.execute() ici émettent la chaîne donnée au
    script de sortie.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Exécuter les migrations en mode 'en ligne'.

    Dans ce scénario, nous devons créer un Engine
    et associer une connexion avec le contexte.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
