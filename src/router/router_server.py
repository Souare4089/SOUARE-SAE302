import sys
import socket
import json
import psutil
from src.common.crypto import RSAEncryption
from src.common.onion import OnionRouter

MASTER_IP = "127.0.0.1"
MASTER_PORT = 9000


class RouterServer:
    """
    ROUTEUR TOR (SAE 302)
    --------------------------------------
    - Génère ses clés RSA
    - S’enregistre auprès du MASTER
    - Déchiffre UNE couche d’oignon
    - Transmet au prochain saut
    - Ou envoie au client final (A ou B)
    """

    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port

        # Génération des clés RSA
        rsa = RSAEncryption()
        self.public_key, self.private_key = rsa.generate_keys()

        self.onion = OnionRouter()

        # Enregistrement automatique auprès du MASTER
        self.register_to_master()

    # ============================================================
    #  LIBÉRER LE PORT S’IL EST DÉJÀ UTILISÉ
    # ============================================================
    def free_port(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.net_connections(kind='inet'):
                    if conn.laddr.port == self.port:
                        print(f"[ROUTER {self.name}] ⚠ Port {self.port} occupé, arrêt PID {proc.pid}")
                        proc.kill()
                        return
            except Exception:
                continue

    # ============================================================
    #  ENREGISTREMENT AUPRÈS DU MASTER
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
    #  DÉMARRAGE DU ROUTEUR
    # ============================================================
    def start(self):
        self.free_port()

        print(f"[ROUTER {self.name}] En écoute sur {self.host}:{self.port}")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

            # =============================
            # DESTINATAIRES FINAUX
            # =============================
            if next_hop == "clientB":
                print(f"[{self.name}] Envoi au destinataire final (clientB).")
                self.send_to_clientB(payload)
                conn.sendall(b"OK")
                conn.close()
                continue

            if next_hop == "clientA":
                print(f"[{self.name}] Envoi au destinataire final (clientA).")
                self.send_to_clientA(payload)
                conn.sendall(b"OK")
                conn.close()
                continue

            # =============================
            # ROUTEUR SUIVANT
            # =============================
            if next_hop is None:
                print(f"[{self.name}] ❌ next_hop invalide, abandon.")
                conn.close()
                continue

            result = self.forward_to_next(next_hop, payload)
            conn.sendall(result.encode())
            conn.close()

    # ============================================================
    #  TRANSMISSION AU ROUTEUR SUIVANT
    # ============================================================
    def forward_to_next(self, next_name, payload):
        try:
            port = 8000 + int(next_name.replace("router", ""))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", port))
                s.sendall(payload.encode())
                reply = s.recv(4096).decode()
                return reply
        except Exception as e:
            return f"[{self.name}] ERREUR : {e}"

    # ============================================================
    #  ENVOI AUX CLIENTS FINAUX
    # ============================================================
    def send_to_clientB(self, msg):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9100))
            s.sendall(msg.encode())

    def send_to_clientA(self, msg):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9001))
            s.sendall(msg.encode())


# ============================================================
#  LANCEMENT DU ROUTEUR
# ============================================================
if __name__ == "__main__":
    """
    Usage :
    python -m src.router.router_server router1 127.0.0.1 8001
    """

    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])

    router = RouterServer(name, host, port)
    router.start()
