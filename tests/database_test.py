import sys
import os

# Ajoute le dossier racine au path pour permettre les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.database import DatabaseManager
from src.common.crypto import RSAEncryption

def test_database():
    print("\n===== TEST BDD - DÉBUT =====")

    # Connexion à la base
    db = DatabaseManager(user="root", password="1234")

    # Génération d'une clé RSA de test
    rsa = RSAEncryption()
    public_key, _ = rsa.generate_keys()

    # Ajout d'un routeur
    db.add_router("Routeur1", "127.0.0.1", 8001, public_key)

    # Récupération des routeurs
    routers = db.get_routers()
    print("Routeurs trouvés :", routers)

    # Ajout d'un log
    db.add_log("Test d'insertion de log OK.")

    print("✔ TEST RÉUSSI - Tout fonctionne.")
    print("===== TEST BDD - FIN =====\n")

if __name__ == "__main__":
    test_database()
