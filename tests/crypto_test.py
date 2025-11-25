# Configuration du chemin pour importer les modules src
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import de la classe RSAEncryption
from src.common.crypto import RSAEncryption

def test_rsa():
    """Test complet du chiffrement RSA"""
    print("Test du chiffrement RSA...")
    
    # Création d'une instance RSA
    rsa = RSAEncryption()
    
    # Génération des clés
    public_key, private_key = rsa.generate_keys()
    print("Clés générées avec succès")
    
    # Message à chiffrer (court pour les tests)
    message = "AB"
    print(f"Message original: {message}")
    
    # Chiffrement avec la clé publique
    encrypted = rsa.encrypt(message, public_key)
    print(f"Message chiffré: {encrypted}")
    
    # Déchiffrement avec la clé privée
    decrypted = rsa.decrypt(encrypted, private_key)
    print(f"Message déchiffré: {decrypted}")
    
    # Vérification
    if message == decrypted:
        print("SUCCES : Le chiffrement/déchiffrement fonctionne correctement")
    else:
        print("ECHEC : Probleme avec le chiffrement")

# Point d'entrée
if __name__ == "__main__":
    test_rsa()