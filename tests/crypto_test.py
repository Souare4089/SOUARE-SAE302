# Configuration du chemin pour importer les modules src
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import de la classe RSAEncryption
from src.common.crypto import RSAEncryption
import time  # Pour mesurer le temps des opérations (optionnel)

def test_rsa():
    """Test complet du chiffrement RSA."""

    print("\n===== TEST RSA - DÉBUT =====")

    rsa = RSAEncryption()

    # Mesure du temps pour générer les clés
    start = time.time()
    public_key, private_key = rsa.generate_keys()
    end = time.time()

    print(f"Clés générées.")
    print(f"Clé publique : {public_key}")
    print(f"Clé privée  : {private_key}")
    print(f"Temps de génération : {end - start:.4f} secondes\n")

    # Message simple utilisé pour le test
    message = "AB"
    print(f"Message original : {message}")

    # Chiffrement
    encrypted = rsa.encrypt(message, public_key)
    print(f"Message chiffré : {encrypted}")

    # Déchiffrement
    decrypted = rsa.decrypt(encrypted, private_key)
    print(f"Message déchiffré : {decrypted}")

    # Vérification
    if message == decrypted:
        print("✔ SUCCÈS : Le chiffrement/déchiffrement fonctionne correctement.\n")
    else:
        print("✘ ÉCHEC : Le résultat ne correspond pas au message original.\n")

    # Test sur les entiers
    print("Test du chiffrement d'un entier...")
    nombre_test = 12345

    encrypted_num = rsa.encrypt_number(nombre_test, public_key)
    decrypted_num = rsa.decrypt_number(encrypted_num, private_key)

    print(f"Nombre original  : {nombre_test}")
    print(f"Nombre chiffré   : {encrypted_num}")
    print(f"Nombre déchiffré : {decrypted_num}")

    if nombre_test == decrypted_num:
        print("✔ SUCCÈS : Le chiffrement/déchiffrement d'entier fonctionne.\n")
    else:
        print("✘ ÉCHEC : Problème dans encrypt_number/decrypt_number.\n")

    print("===== TEST RSA - FIN =====\n")


# Point d'entrée
if __name__ == "__main__":
    test_rsa()
