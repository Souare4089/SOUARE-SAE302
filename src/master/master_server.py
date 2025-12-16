import socket
import json
import psutil
import time
from src.common.database import DatabaseManager


class MasterServer:
    """
    MASTER SERVER (SAE 302)
    """

    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.db = DatabaseManager()

    # ============================================================
    # LIBÉRATION DU PORT
    # ============================================================
    def free_port(self):
        for proc in psutil.process_iter(["pid"]):
            try:
                for conn in proc.connections(kind="inet"):
                    if conn.laddr.port == self.port:
                        proc.kill()
                        time.sleep(1)
                        return
            except Exception:
                pass

    # ============================================================
    # DÉMARRAGE
    # ============================================================
    def start(self):
        print(f"[MASTER] Démarrage sur {self.host}:{self.port}")
        self.free_port()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((self.host, self.port))
            server.listen()
            print("[MASTER] En attente des clients / routeurs...")

            while True:
                conn, addr = server.accept()
                req = conn.recv(8192).decode()
                response = self.process_request(req)
                conn.sendall(response.encode())
                conn.close()

    # ============================================================
    # TRAITEMENT DES REQUÊTES
    # ============================================================
    def process_request(self, req):

        # ROUTEUR → MASTER
        if req.startswith("REGISTER_ROUTER"):
            try:
                data = json.loads(req.replace("REGISTER_ROUTER ", ""))

                name = data["name"]
                ip = data["ip"]
                port = data["port"]
                public_key = tuple(data["public_key"])

                # ⭐ SUPPRESSION AUTOMATIQUE AVANT AJOUT
                self.db.remove_router(name)
                self.db.add_router(name, ip, port, public_key)

                print(f"[MASTER] ✔ Routeur {name} enregistré (mise à jour).")
                return "OK"

            except Exception as e:
                return f"[MASTER] ERREUR REGISTER : {e}"

        # CLIENT A → MASTER
        if req == "GET_ROUTERS":
            routers = self.db.get_routers()
            print(f"[MASTER] {len(routers)} routeurs envoyés.")
            return json.dumps(routers)

        return "[MASTER] ERREUR : Commande inconnue."


if __name__ == "__main__":
    MasterServer().start()
