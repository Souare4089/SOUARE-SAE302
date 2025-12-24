import socket
import json
import random
from src.common.onion import OnionRouter

MASTER_IP = "127.0.0.1"
MASTER_PORT = 9000
LISTEN_PORT = 9100


class ClientB:
    """
    Client B :
    - peut recevoir un message via le réseau TOR
    - peut envoyer un message vers Client A
    """

    def __init__(self):
        self.onion = OnionRouter()

    # ===============================
    # Récupération des routeurs
    # ===============================
    def get_routers(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((MASTER_IP, MASTER_PORT))
            s.sendall(b"GET_ROUTERS")
            resp = s.recv(8192).decode()
        return json.loads(resp)

    # ===============================
    # Envoi du message
    # ===============================
    def send_message(self, message, debug=False):
        routers = self.get_routers()

        if debug:
            print("[CLIENT B] Routeurs disponibles :", routers)

        selected = random.sample(routers, 3)
        chain = [r["name"] for r in selected]

        if debug:
            print("[CLIENT B] Chaîne choisie :", chain)

        keys = {r["name"]: r["public_key"] for r in selected}

        onion_msg = self.onion.create_onion_message(
            message,
            "clientA",
            chain,
            keys
        )

        first = selected[0]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((first["ip"], first["port"]))
            s.sendall(onion_msg.encode())

    # ===============================
    # Réception
    # ===============================
    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", LISTEN_PORT))
            s.listen()
            print(f"[CLIENT B] En écoute sur {LISTEN_PORT}")

            while True:
                conn, _ = s.accept()
                msg = conn.recv(4096).decode()
                print(f"\n📩 MESSAGE FINAL REÇU : {msg}\n")
                conn.close()


# ======================================================
# FONCTIONS PUBLIQUES (POUR GUI)
# ======================================================
def send_message(message):
    ClientB().send_message(message)   # debug désactivé pour le GUI


def listen():
    ClientB().listen()


# ======================================================
# MODE CLI
# ======================================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2 or sys.argv[1] not in ["send", "listen"]:
        print("Usage : python clientB.py send | listen")
        sys.exit(1)

    client = ClientB()

    if sys.argv[1] == "send":
        msg = input("Message à envoyer : ")
        client.send_message(msg, debug=True)  # debug UNIQUEMENT en CLI
    else:
        client.listen()
