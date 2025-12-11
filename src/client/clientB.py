import socket
import psutil


class ClientB:
    """
    CLIENT B = destinataire final du message.
    """

    def __init__(self, host="127.0.0.1", port=9100):
        self.host = host
        self.port = port

    # ============================================================
    #  LIBÉRER LE PORT (compatible Windows)
    # ============================================================
    def free_port(self):
        """Tue tout processus utilisant déjà le port."""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                conns = proc.net_connections(kind='inet')  # version correcte
                for conn in conns:
                    if conn.laddr.port == self.port:
                        print(f"[CLIENT B] Port {self.port} occupé par PID {proc.pid}, arrêt du processus.")
                        proc.kill()
                        return
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

    # ============================================================
    #  LANCEMENT DU SERVEUR
    # ============================================================
    def start(self):
        """Démarre le serveur et attend le message final."""

        # Libérer le port avant bind()
        self.free_port()

        print(f"[CLIENT B] Démarrage sur {self.host}:{self.port}")

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # OPTION QUI RÈGLE LE PROBLÈME :
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind((self.host, self.port))
        server.listen()

        print(f"[CLIENT B] En écoute...")

        while True:
            conn, addr = server.accept()
            data = conn.recv(4096).decode()

            print(f"\n📩 MESSAGE FINAL REÇU : {data}\n")

            conn.sendall(b"OK")
            conn.close()


# Lancement direct
if __name__ == "__main__":
    b = ClientB()
    b.start()
