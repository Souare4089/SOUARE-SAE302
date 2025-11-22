import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.common.sockets import ServerSocket
import threading
import time

def test_server():
    server = ServerSocket(port=8080)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(2)
    print("Serveur prêt pour les tests")

if __name__ == "__main__":
    test_server()
    input("Appuyez sur Entrée pour arrêter...")