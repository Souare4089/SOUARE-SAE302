# ================================================================
#   TEST DU ROUTAGE EN OIGNON – VERSION COMPATIBLE RSA CHAR-BY-CHAR
# ================================================================

import sys
import os

# Permet au test d'importer le dossier src/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.crypto import RSAEncryption
from src.common.onion import OnionRouter


def test_onion_routing():

    print("\n===== TEST ROUTAGE EN OIGNON - DÉBUT =====")

    # ------------------------------------------------------------
    #   1) Création des routeurs + clés RSA
    # ------------------------------------------------------------
    r1 = RSAEncryption()
    r2 = RSAEncryption()
    r3 = RSAEncryption()

    pub1, priv1 = r1.generate_keys()
    pub2, priv2 = r2.generate_keys()
    pub3, priv3 = r3.generate_keys()

    router_chain = ["router1", "router2", "router3"]
    router_public_keys = {
        "router1": pub1,
        "router2": pub2,
        "router3": pub3,
    }

    onion = OnionRouter()

    message = "A"
    destination = "B"

    print("Message original :", message)
    print("Destination      :", destination)

    # ------------------------------------------------------------
    #   2) Création du message en oignon
    # ------------------------------------------------------------
    onion_msg = onion.create_onion_message(
        message, destination, router_chain, router_public_keys
    )

    print("\nMessage envoyé au routeur 1 :")
    print(onion_msg, "\n")

    # ------------------------------------------------------------
    #   3) Routeur 1 déchiffre
    # ------------------------------------------------------------
    next1, layer1 = onion.process_onion_layer(onion_msg, priv1)

    print("[R1] next hop :", next1)
    print("[R1] payload  :", layer1, "\n")

    assert next1 == "router2", "Routeur1 doit envoyer vers router2"

    # ------------------------------------------------------------
    #   4) Routeur 2 déchiffre
    # ------------------------------------------------------------
    next2, layer2 = onion.process_onion_layer(layer1, priv2)

    print("[R2] next hop :", next2)
    print("[R2] payload  :", layer2, "\n")

    assert next2 == "router3", "Routeur2 doit envoyer vers router3"

    # ------------------------------------------------------------
    #   5) Routeur 3 déchiffre (couche finale)
    # ------------------------------------------------------------
    next3, final_data = onion.process_onion_layer(layer2, priv3)

    print("[R3] next hop :", next3)
    print("[R3] message final brut :", final_data, "\n")

    # Dans la dernière couche :
    # next3 = "B"
    # final_data = "A"

    dest = next3
    msg = final_data

    assert dest == destination, "La destination finale doit être B"
    assert msg == message, "Le message final doit être A"

    print("✔ SUCCÈS : Routage en oignon fonctionnel !")
    print("===== TEST ROUTAGE EN OIGNON – FIN =====\n")


if __name__ == "__main__":
    test_onion_routing()
