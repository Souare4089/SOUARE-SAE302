# Configuration du chemin pour importer les modules src
import sys
import os
# Ajoute le répertoire parent au chemin Python pour résoudre les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import de la classe Database depuis le module database
from src.common.database import Database

def test_database():
    """Test de création et connexion à la base de données"""
    # Création d'une instance Database
    db = Database()
    
    # Création de la base de données et des tables
    if db.create_database():
        # Tentative de connexion à la base créée
        connection = db.connect()
        if connection:
            print("✅ Base de données créée et connectée avec succès")
            # Fermeture propre de la connexion
            connection.close()
        else:
            print("❌ Erreur de connexion après création")
    else:
        print("❌ Erreur lors de la création de la base")

# Point d'entrée du programme de test
if __name__ == "__main__":
    # Lancement du test complet de la base de données
    test_database()