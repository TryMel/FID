"""
init_db.py
===========
Script d'initialisation de la base de données.
Crée toutes les tables selon les modèles SQLAlchemy.
À exécuter une seule fois au démarrage ou après suppression de la DB.

Usage : python init_db.py
"""
import sys
import os

# S'assurer que le dossier backend est dans le path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base

# Importer TOUS les modèles pour que SQLAlchemy les connaisse
from app.models import (
    Utilisateur,
    Profil,
    Experience,
    Diplome,
    Certification,
    Competence,
    Projet,
    Collaboration,
    Candidature,
    Avis,
    Paiement,
    ScoreConfiance,
    CodeQR,
    Verification,
    ValidationSociale,
    CV,
)

def initialiser_base():
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Toutes les tables ont été créées avec succès.")
    
    # Afficher les tables créées
    from sqlalchemy import inspect
    inspecteur = inspect(engine)
    tables = inspecteur.get_table_names()
    print(f"\nTables créées ({len(tables)}) :")
    for table in sorted(tables):
        colonnes = [c['name'] for c in inspecteur.get_columns(table)]
        print(f"  • {table} ({len(colonnes)} colonnes)")

if __name__ == "__main__":
    initialiser_base()
