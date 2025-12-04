# Configuration du chemin pour importer les modules src
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des classes nécessaires
from src.common.onion import OnionRouter
from src.common.crypto import RSAEncryption

def test_onion_routing():
    """Test complet du routage en oignon"""
    print("Test du routage en oignon...")
    
    # Création des routeurs et génération de leurs clés
    router1 = RSAEncryption()
    router2 = RSAEncryption() 
    router3 = RSAEncryption()
    
    public_key1, private_key1 = router1.generate_keys()
    public_key2, private_key2 = router2.generate_keys()
    public_key3, private_key3 = router3.generate_keys()
    
    print("Clés des routeurs générées")
    
    # Configuration de la chaîne de routeurs
    router_chain = ["router1", "router2", "router3"]
    router_public_keys = {
        "router1": public_key1,
        "router2": public_key2, 
        "router3": public_key3
    }
    
    # Création du routeur oignon
    onion_router = OnionRouter()
    
    # Message à envoyer (très court pour les tests)
    message = "A"
    destination = "B"
    
    print(f"Message original: {message}")
    print(f"Destination: {destination}")
    print(f"Chaine de routeurs: {router_chain}")
    
    # Création du message en oignon
    onion_message = onion_router.create_onion_message(
        message, destination, router_chain, router_public_keys
    )
    print(f"Message oignon créé: {onion_message}")
    
    # Simulation du parcours à travers les routeurs
    
    # Routeur 1 déchiffre la première couche
    next_hop1, payload1 = onion_router.process_onion_layer(onion_message, private_key1)
    print(f"Routeur 1 - Prochain saut: {next_hop1}, Payload restant: {payload1}")
    
    # Routeur 2 déchiffre la deuxième couche  
    next_hop2, payload2 = onion_router.process_onion_layer(payload1, private_key2)
    print(f"Routeur 2 - Prochain saut: {next_hop2}, Payload restant: {payload2}")
    
    # Routeur 3 déchiffre la dernière couche
    next_hop3, final_message = onion_router.process_onion_layer(payload2, private_key3)
    print(f"Routeur 3 - Destination: {next_hop3}, Message final: {final_message}")
    
    # Vérification du résultat
    if final_message == f"{destination}|{message}":
        print("SUCCES : Le routage en oignon fonctionne correctement")
        print(f"Message délivré à {destination}: {message}")
    else:
        print(f"ECHEC : Attendu '{destination}|{message}', obtenu '{final_message}'")

# Point d'entrée
if __name__ == "__main__":
    test_onion_routing()