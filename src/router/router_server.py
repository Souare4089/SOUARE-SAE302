import sys
import os
import socket
import json
import psutil
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.crypto import RSAEncryption
from src.common.onion import OnionRouter


MASTER_IP = "127.0.0.1"
MASTER_PORT = 9000


class RouterServer:
    """
    ROUTEUR TOR (SAE)
    --------------------------------------
    - génère ses clés RSA
    - s’enregistre auprès du MASTER
    - déchiffre UNE couche oignon
    - renvoie vers le prochain routeur
    - ou vers clientB (destinataire final)
    """

    def __init__(self, name, host, port, next_router=None):
        self.name = name
        self.host = host
        self.port = port
        self.next_router = next_router

        # Génération des clés RSA
        rsa = RSAEncryption()
        self.public_key, self.private_key = rsa.generate_keys()

        self.onion = OnionRouter()

        # Enregistrement automatique auprès du MASTER
        self.register_to_master()

    # ============================================================
    #     Enregistrement automatique auprès du MASTER
    # ============================================================
    def register_to_master(self):
        try:
            data = {
                "name": self.name,
                "ip": self.host,
                "port": self.port,
                "public_key": list(self.public_key)
            }

            msg = "REGISTER_ROUTER " + json.dumps(data)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((MASTER_IP, MASTER_PORT))
                s.sendall(msg.encode())

            print(f"[ROUTER {self.name}] ✔ Enregistré auprès du MASTER.")

        except Exception as e:
            print(f"[ROUTER {self.name}] ❌ ERREUR REGISTER: {e}")

    # ============================================================
    #         LIBÉRATION AUTOMATIQUE DU PORT (WINDOWS)
    # ============================================================
    def free_port(self):
        """Libère le port si déjà utilisé (évite WinError 10048)."""
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                for conn in proc.net_connections(kind="inet"):
                    if conn.laddr.port == self.port:
                        print(f"[ROUTER {self.name}] ⚠ Port {self.port} occupé, arrêt PID {proc.pid}")
                        proc.kill()
                        time.sleep(1)
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    # ============================================================
    #                     DÉMARRAGE ROUTEUR
    # ============================================================
    def start(self):
        print(f"[ROUTER {self.name}] En écoute sur {self.host}:{self.port}")

        # ⭐ libération automatique du port
        self.free_port()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()

            while True:
                conn, addr = server.accept()
                data = conn.recv(4096).decode()

                print(f"[{self.name}] Couche reçue : {data[:80]}...")

                next_hop, payload = self.onion.process_onion_layer(
                    data, self.private_key
                )

                print(f"[{self.name}] next_hop = {next_hop}")

                # Dernier routeur → Client B
                if next_hop == "clientB":
                    print(f"[{self.name}] Envoi au destinataire final (clientB).")
                    self.send_to_clientB(payload)
                    conn.sendall(b"OK")
                    conn.close()
                    continue

                # Transmission au routeur suivant
                result = self.forward_to_next(next_hop, payload)
                conn.sendall(result.encode())
                conn.close()

    # ============================================================
    #       Transmission au routeur suivant
    # ============================================================
    def forward_to_next(self, next_name, payload):
        port = 8000 + int(next_name.replace("router", ""))

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", port))
                s.sendall(payload.encode())
                reply = s.recv(4096).decode()
                return reply
        except Exception as e:
            return f"[{self.name}] ERREUR : {e}"

    # ============================================================
    #       Envoi au clientB (destinataire final)
    # ============================================================
    def send_to_clientB(self, msg):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9100))
            s.sendall(msg.encode())


# =================================================================
#   LANCEMENT AUTOMATIQUE PAR ARGUMENTS
# =================================================================
if __name__ == "__main__":
    """
    Utilisation :
        python router_server.py router1 127.0.0.1 8001
        python router_server.py router3 127.0.0.1 8003
    """

    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    server = RouterServer(name, host, port)
    server.start()
