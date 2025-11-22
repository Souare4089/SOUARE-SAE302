# Ajout du chemin pour trouver les modules src
import sys
import os
# Ajoute le répertoire parent au chemin Python pour importer src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import du module socket pour la communication réseau
import socket

def test_client():
    # Création d'un socket client TCP/IP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connexion au serveur sur localhost port 8080
    client.connect(('localhost', 8080))
    
    # Envoi d'un message au serveur (encodé en bytes)
    client.send("Hello serveur".encode())
    
    # Réception de la réponse du serveur (1024 bytes max)
    response = client.recv(1024).decode()
    
    # Affichage de la réponse reçue
    print(f"Réponse du serveur: {response}")
    
    # Fermeture de la connexion
    client.close()

# Point d'entrée du programme
if __name__ == "__main__":
    # Lancement du test client
    test_client()