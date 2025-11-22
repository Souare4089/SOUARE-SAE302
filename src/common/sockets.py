# Import des modules nécessaires
import socket  # Pour la communication réseau
import threading  # Pour gérer plusieurs clients en parallèle

class ServerSocket:
    def __init__(self, host='localhost', port=8080):
        # Configuration du serveur
        self.host = host  # Adresse d'écoute
        self.port = port  # Port d'écoute
        # Création du socket TCP/IP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def start(self):
        # Association du socket à l'adresse et port
        self.socket.bind((self.host, self.port))
        # Démarrage de l'écoute (max 5 connexions en attente)
        self.socket.listen(5)
        print(f"Serveur démarré sur {self.host}:{self.port}")
        
        # Boucle principale d'acceptation des connexions
        while True:
            # Accepte une nouvelle connexion client
            client_socket, address = self.socket.accept()
            print(f"Connexion de {address}")
            
            # Crée un nouveau thread pour gérer ce client
            client_thread = threading.Thread(
                target=self.handle_client,  # Fonction à exécuter
                args=(client_socket, address)  # Arguments à passer
            )
            client_thread.start()  # Démarre le thread
    
    def handle_client(self, client_socket, address):
        # Gère la communication avec un client spécifique
        try:
            while True:
                # Reçoit le message du client (max 1024 bytes)
                message = client_socket.recv(1024).decode()
                if not message:  # Si message vide, connexion fermée
                    break
                print(f"Message de {address}: {message}")
                # Envoie un accusé de réception
                client_socket.send("Message reçu".encode())
        finally:
            # Ferme la connexion avec le client
            client_socket.close()
            