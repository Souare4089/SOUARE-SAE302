import socket
import json
import random
import argparse
import psutil
from src.common.onion import OnionRouter


MASTER_IP = "127.0.0.1"
MASTER_PORT = 9000


class ClientB:
    """
    CLIENT B (SAE 302)
    --------------------------------------
    - Peut RECEVOIR un message (listen)
    - Peut ENVOYER un message (send)
    - Utilise le même routage en oignon que Client A
    """

    def __init__(self, host="127.0.0.1", port=9100):
        self.host = host
        self.port = port
        self.onion = OnionRouter()

    # ============================================================
    #  LIBÉRER LE PORT (Windows / Linux compatible)
    # ============================================================
    def free_port(self):
        """Tue tout processus utilisant déjà le port."""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.net_connections(kind='inet'):
                    if conn.laddr.port == self.port:
                        proc.kill()
                        return
            except Exception:
                continue

    # ============================================================
    #  MODE LISTEN : réception du message final
    # ============================================================
    def listen(self):
        self.free_port()

        print(f"[CLIENT B] Démarrage en mode LISTEN sur {self.host}:{self.port}")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen()

        print("[CLIENT B] En écoute...")

        while True:
            conn, addr = server.accept()
            data = conn.recv(4096).decode()

            print(f"\n📩 MESSAGE FINAL REÇU : {data}\n")

            conn.sendall(b"OK")
            conn.close()

    # ============================================================
    #  Récupération des routeurs depuis le MASTER
    # ============================================================
    def get_routers(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((MASTER_IP, MASTER_PORT))
            s.sendall(b"GET_ROUTERS")
            resp = s.recv(8192).decode()

        return json.loads(resp)

    # ============================================================
    #  Envoi du message au premier routeur
    # ============================================================
    def send_to_router(self, ip, port, msg):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(msg.encode())

        print("[CLIENT B] Message envoyé au réseau TOR.")

    # ============================================================
    #  MODE SEND : envoi d’un message anonymisé
    # ============================================================
    def send(self):
        message = input("Message à envoyer : ")

        routers = self.get_routers()
        print("[CLIENT B] Routeurs disponibles :", routers)

        selected = random.sample(routers, 3)
        router_chain = [r["name"] for r in selected]
        router_keys = {r["name"]: r["public_key"] for r in selected}

        print("[CLIENT B] Chaîne choisie :", router_chain)

        onion_msg = self.onion.create_onion_message(
            message=message,
            destination="clientA",
            router_chain=router_chain,
            router_public_keys=router_keys
        )

        first_router = selected[0]
        self.send_to_router(first_router["ip"], first_router["port"], onion_msg)


# ============================================================
#  POINT D’ENTRÉE (ARGPARSE PRO)
# ============================================================
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Client B - SAE 302 (envoi / réception via routage en oignon)"
    )

    parser.add_argument(
        "--mode",
        choices=["listen", "send"],
        required=True,
        help="Mode de fonctionnement du client"
    )

    args = parser.parse_args()

    client = ClientB()

    if args.mode == "listen":
        client.listen()
    elif args.mode == "send":
        client.send()

