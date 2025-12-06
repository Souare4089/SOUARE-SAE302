import sys
import os

# Pour pouvoir importer src/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.router.router import Router
from src.common.onion import OnionRouter


def test_router_dechiffrement():
    print("\n===== TEST ROUTER - DÉBUT =====")

    # Création d'un routeur "virtuel" juste pour le test
    router = Router("router1", host="127.0.0.1", port=8001)

    # On va construire une couche d'oignon compatible avec OnionRouter
    onion = OnionRouter()

    # Texte de la couche : next_hop|payload
    # Ici, on simule : le routeur1 doit envoyer vers router2 avec "12345" comme payload
    layer_text = "router2|12345"

    # On chiffre cette couche EXACTEMENT comme dans create_onion_message :
    encrypted_list = onion._encrypt_layer(layer_text, router.public_key)

    # On encode en chaîne de caractères "a,b,c,d"
    encrypted_str = ",".join(str(x) for x in encrypted_list)

    print("[TEST] Couche chiffrée envoyée au routeur1 :")
    print(encrypted_str[:100], "...\n")

    # Maintenant, on demande au routeur (en réalité à OnionRouter) de traiter cette couche
    next_hop, payload = onion.process_onion_layer(encrypted_str, router.private_key)

    print("[TEST] next_hop obtenu  :", next_hop)
    print("[TEST] payload obtenu   :", payload)

    # Vérifications
    assert next_hop == "router2", "Le prochain saut attendu est router2"
    assert payload == "12345", "Le payload attendu est 12345"

    print("✔ Test routeur OK")
    print("===== FIN TEST ROUTER =====\n")


if __name__ == "__main__":
    test_router_dechiffrement()
