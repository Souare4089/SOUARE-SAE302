import socket
import json
import random
from src.common.onion import OnionRouter

class ClientA:
    """
    CLIENT A (expéditeur)
    - demande la liste des routeurs au MASTER
    - choisit une chaîne de routeurs
    - construit le message en oignon
    - envoie au premier routeur
    """

    def __init__(self, master_ip="127.0.0.1", master_port=9000):
        self.master_ip = master_ip
        self.master_port = master_port
        self.onion = OnionRouter()

    # ------------------------------------------------------------
    # Récupérer la liste des routeurs depuis le MASTER
    # ------------------------------------------------------------
    def get_routers(self):
        req = "GET_ROUTERS"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.master_ip, self.master_port))
            s.sendall(req.encode())
            resp = s.recv(4096).decode()
        return json.loads(resp)

    # ------------------------------------------------------------
    # Envoyer un message au routeur 1
    # ------------------------------------------------------------
    def send_to_router(self, ip, port, msg):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(msg.encode())
        print("[CLIENT A] Message envoyé au réseau TOR.")

    # ------------------------------------------------------------
    # Envoyer un message avec routage en oignon
    # ------------------------------------------------------------
    def send_message(self, message, destination="clientB"):
        routers = self.get_routers()
        print("[CLIENT A] Routeurs disponibles :", routers)

        # choisir 3 routeurs aléatoires
        selected = random.sample(routers, 3)
        router_chain = [r["name"] for r in selected]
        router_keys = {r["name"]: r["public_key"] for r in selected}

        print("[CLIENT A] Chaîne choisie :", router_chain)

        onion_msg = self.onion.create_onion_message(
            message,
            destination,
            router_chain,
            router_keys
        )

        # envoyer au premier routeur
        first_router = selected[0]
        self.send_to_router(first_router["ip"], first_router["port"], onion_msg)


if __name__ == "__main__":
    client = ClientA()
    msg = input("Message à envoyer : ")
    client.send_message(msg)
