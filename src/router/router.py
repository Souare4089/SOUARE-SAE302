import socket
import threading

from src.common.crypto import RSAEncryption
from src.common.onion import OnionRouter


class Router:
    """
    Classe représentant un routeur du réseau.
    - génère ses clés
    - écoute sur un port
    - reçoit un message en oignon
    - déchiffre une seule couche
    - envoie au prochain routeur
    """

    def __init__(self, name, host="127.0.0.1", port=0):
        self.name = name
        self.host = host
        self.port = port

        # Modules cryptographiques déjà créés
        self.crypto = RSAEncryption()
        self.onion = OnionRouter()

        # Génération des clés RSA
        self.public_key, self.private_key = self.crypto.generate_keys()

    # ===============================================================
    #                   SERVEUR ROUTEUR (ÉCOUTE)
    # ===============================================================
    def start(self):
        """Démarre le serveur du routeur."""

        print(f"[{self.name}] Démarrage du routeur sur {self.host}:{self.port} ...")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)

        print(f"[{self.name}] En écoute... (CTRL+C pour arrêter)")

        while True:
            client_socket, addr = server.accept()
            print(f"[{self.name}] Connexion reçue de {addr}")

            # Thread : chaque message est traité indépendamment
            t = threading.Thread(target=self.handle_connection, args=(client_socket,))
            t.start()

    # ===============================================================
    #                   RÉCEPTION D'UN MESSAGE
    # ===============================================================
    def handle_connection(self, client_socket):

        received = client_socket.recv(10000).decode()
        print(f"[{self.name}] Message reçu : {received[:80]}...")

        # Déchiffrer UNE couche d’oignon
        next_hop, payload = self.onion.process_onion_layer(received, self.private_key)

        print(f"[{self.name}] Prochain saut = {next_hop}")

        if next_hop is None:
            # Dernière couche → message final
            print(f"[{self.name}] Message final reçu : {payload}")
            client_socket.close()
            return

        # ============================================================
        #               ENVOI AU ROUTEUR SUIVANT
        # ============================================================
        next_host = "127.0.0.1"
        next_port = int(next_hop.replace("router", "80"))  # ex : router2 → port 802

        print(f"[{self.name}] Transmission vers {next_hop} ({next_host}:{next_port})")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((next_host, next_port))
        sock.send(payload.encode())
        sock.close()

        client_socket.close()
