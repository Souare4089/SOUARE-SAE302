import socket
import json
import psutil
from src.common.database import DatabaseManager
import time


class MasterServer:
    """
    MASTER SERVER (SAE 302)
    ----------------------------------------------------
    Rôle du MASTER :
      ✓ Fournir la liste des routeurs au client A
      ✓ Recevoir l’enregistrement automatique des routeurs
      ✗ Ne crée PAS d'oignon
      ✗ Ne choisit PAS les routeurs
      ✗ Ne contacte PAS les routeurs
    """

    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.db = DatabaseManager()   # connexion BDD

    # ============================================================
    #   LIBÉRATION AUTOMATIQUE DU PORT (Windows compatible)
    # ============================================================
    def free_port(self):
        """Tue le processus qui occupe le port (Windows compatible)."""
        for proc in psutil.process_iter(["pid", "name"]):

            try:
                conns = proc.connections(kind="inet")
            except Exception:
                continue

            for conn in conns:
                if conn.laddr.port == self.port:
                    print(f"[MASTER] ⚠ Port {self.port} occupé par PID {proc.pid}, arrêt du processus...")
                    proc.kill()
                    time.sleep(1)  # indispensable sous Windows
                    return True

        return False

    # ============================================================
    #                   DÉMARRAGE DU MASTER
    # ============================================================
    def start(self):
        print(f"[MASTER] Démarrage sur {self.host}:{self.port}")

        self.free_port()  # libère le port avant bind()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

            try:
                server.bind((self.host, self.port))
            except OSError:
                print(f"[MASTER] ❌ Port {self.port} encore bloqué. Arrêt.")
                return

            server.listen()
            print("[MASTER] En attente des clients / routeurs...")

            while True:
                conn, addr = server.accept()
                print(f"[MASTER] Connexion reçue : {addr}")

                req = conn.recv(8192).decode()

                response = self.process_request(req)
                conn.sendall(response.encode())
                conn.close()

    # ============================================================
    #         TRAITEMENT DES COMMANDES CLIENT / ROUTEUR
    # ============================================================
    def process_request(self, req):

        # -----------------------------------------
        # 1) Routeur s’enregistre automatiquement
        # -----------------------------------------
        if req.startswith("REGISTER_ROUTER"):
            try:
                data = json.loads(req.replace("REGISTER_ROUTER ", ""))

                name = data["name"]
                ip = data["ip"]
                port = data["port"]
                public_key = tuple(data["public_key"])

                self.db.add_router(name, ip, port, public_key)

                print(f"[MASTER] ✔ Routeur {name} enregistré.")
                return "OK"

            except Exception as e:
                return f"[MASTER] ERREUR REGISTER: {e}"

        # -----------------------------------------
        # 2) Client A demande la liste des routeurs
        # -----------------------------------------
        if req == "GET_ROUTERS":
            routers = self.db.get_routers()
            print(f"[MASTER] {len(routers)} routeurs envoyés.")
            return json.dumps(routers)

        # -----------------------------------------
        # 3) Commande inconnue
        # -----------------------------------------
        return "[MASTER] ERREUR : Commande inconnue."


# ============================================================
#                 LANCEMENT DIRECT
# ============================================================
if __name__ == "__main__":
    master = MasterServer()
    master.start()
