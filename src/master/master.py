# Import des modules système
import sys
import os
# Ajout du chemin pour trouver les modules src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des modules PyQt6 pour l'interface graphique et réseau
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QHBoxLayout,
                             QStatusBar)
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PyQt6.QtGui import QFont

# Import de la base de données
from common.database import Database

class ClientHandler(QTcpSocket):
    """Gestionnaire de client utilisant QTcpSocket (non-bloquant)"""
    
    def __init__(self, socket_descriptor, parent=None):
        super().__init__(parent)
        self.setSocketDescriptor(socket_descriptor)
        self.readyRead.connect(self.read_data)
        self.disconnected.connect(self.client_disconnected)
        self.peer_address = self.peerAddress().toString() + ":" + str(self.peerPort())
        
    @pyqtSlot()
    def read_data(self):
        """Lit les données disponibles de manière non-bloquante"""
        try:
            if self.bytesAvailable() > 0:
                data = self.readAll().data().decode('utf-8').strip()
                if data:
                    response = self.process_message(data)
                    self.write(response.encode('utf-8'))
        except Exception as e:
            print(f"Erreur lecture données: {e}")
            
    def process_message(self, message):
        """Traite les messages du client"""
        if message.startswith("GET_ROUTERS"):
            # Simuler une liste de routeurs
            routers = ["router1:9001", "router2:9002", "router3:9003"]
            return f"ROUTERS_LIST|{','.join(routers)}"
        elif message == "PING":
            return "PONG"
        else:
            return "UNKNOWN_COMMAND"
            
    @pyqtSlot()
    def client_disconnected(self):
        """Nettoyage quand le client se déconnecte"""
        self.deleteLater()

class QtTcpServer(QTcpServer):
    """Serveur TCP utilisant les sockets non-bloquants de Qt"""
    
    def __init__(self, log_signal, connection_signal):
        super().__init__()
        self.log_signal = log_signal
        self.connection_signal = connection_signal
        self.newConnection.connect(self.on_new_connection)
        self.clients = []
        
    @pyqtSlot()
    def on_new_connection(self):
        """Gère les nouvelles connexions clients"""
        while self.hasPendingConnections():
            client_socket = self.nextPendingConnection()
            client_handler = ClientHandler(client_socket.socketDescriptor(), self)
            
            client_ip = client_handler.peerAddress().toString()
            client_port = client_handler.peerPort()
            
            self.clients.append(client_handler)
            self.connection_signal.emit(f"Nouvelle connexion: {client_ip}:{client_port}")
            
            # Connecter le signal de déconnexion pour le nettoyage
            client_handler.disconnected.connect(
                lambda: self.client_disconnected(client_handler)
            )
    
    def client_disconnected(self, client):
        """Gère la déconnexion d'un client"""
        if client in self.clients:
            self.clients.remove(client)
            self.log_signal.emit(f"Client déconnecté: {client.peer_address}")
    
    def stop_server(self):
        """Arrête le serveur et ferme toutes les connexions"""
        for client in self.clients:
            client.disconnectFromHost()
        self.close()

class ServerThread(QThread):
    """Thread séparé pour le serveur réseau utilisant QTcpServer"""
    
    log_signal = pyqtSignal(str)
    connection_signal = pyqtSignal(str)
    server_started = pyqtSignal(bool)
    
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.server = None
        self.is_running = False
        
    def run(self):
        """Fonction principale du thread serveur"""
        try:
            # Création du serveur Qt non-bloquant
            self.server = QtTcpServer(self.log_signal, self.connection_signal)
            
            # Démarrage de l'écoute
            if self.server.listen(QHostAddress(self.host), self.port):
                self.is_running = True
                self.log_signal.emit(f"Serveur en écoute sur {self.host}:{self.port}")
                self.server_started.emit(True)
                
                # Boucle d'événements du thread
                self.exec()
            else:
                error_msg = f"Erreur: Impossible de démarrer le serveur - {self.server.errorString()}"
                self.log_signal.emit(error_msg)
                self.server_started.emit(False)
                
        except Exception as e:
            error_msg = f"Erreur critique du serveur: {e}"
            self.log_signal.emit(error_msg)
            self.server_started.emit(False)
            
    def stop(self):
        """Arrête le serveur de manière propre"""
        self.is_running = False
        if self.server:
            self.server.stop_server()
        self.quit()
        self.wait(2000)  # Attendre 2 secondes maximum

class MasterWindow(QMainWindow):
    """Fenêtre principale du serveur maître"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.router_public_keys = {}
        self.server_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface graphique"""
        self.setWindowTitle("Master - Routeur Oignon")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("SERVEUR MAÎTRE - Système de Routage Oignon")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Statut du serveur
        self.status_label = QLabel("Statut: Arrêté")
        layout.addWidget(self.status_label)
        
        # Zone de logs
        logs_label = QLabel("Logs du serveur:")
        layout.addWidget(logs_label)
        
        self.logs_area = QTextEdit()
        self.logs_area.setReadOnly(True)
        self.logs_area.setMaximumHeight(400)
        layout.addWidget(self.logs_area)
        
        # Boutons de contrôle
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Démarrer le serveur")
        self.start_btn.clicked.connect(self.start_server)
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Arrêter le serveur")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        buttons_layout.addWidget(self.stop_btn)
        
        layout.addLayout(buttons_layout)
        
        central_widget.setLayout(layout)
        
        # Barre de statut
        self.statusBar().showMessage("Prêt à démarrer le serveur")
        
        self.log("Interface Master initialisée")
        
    def start_server(self):
        """Démarre le serveur"""
        try:
            # Initialisation de la base de données
            self.db.create_database()
            
            # Création du thread serveur
            self.server_thread = ServerThread('localhost', 8000)
            self.server_thread.log_signal.connect(self.log)
            self.server_thread.connection_signal.connect(self.log)
            self.server_thread.server_started.connect(self.on_server_started)
            self.server_thread.start()
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Statut: Démarrage en cours...")
            
        except Exception as e:
            self.log(f"Erreur démarrage serveur: {e}")
            
    @pyqtSlot(bool)
    def on_server_started(self, success):
        """Callback quand le serveur a démarré"""
        if success:
            self.status_label.setText("Statut: En cours d'exécution")
            self.status_label.setStyleSheet("color: green;")
            self.statusBar().showMessage("Serveur démarré avec succès sur le port 8000")
        else:
            self.status_label.setText("Statut: Erreur de démarrage")
            self.status_label.setStyleSheet("color: red;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        
    def stop_server(self):
        """Arrête le serveur"""
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop()
            self.server_thread = None
            
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Statut: Arrêté")
        self.status_label.setStyleSheet("color: gray;")
        self.statusBar().showMessage("Serveur arrêté")
        self.log("Serveur arrêté par l'utilisateur")
        
    @pyqtSlot(str)
    def log(self, message):
        """Ajoute un message dans les logs"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_area.append(f"[{timestamp}] {message}")
        
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        if self.server_thread and self.server_thread.isRunning():
            self.stop_server()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle('Fusion')
    
    window = MasterWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()