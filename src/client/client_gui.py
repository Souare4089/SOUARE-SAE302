import sys
import socket
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel
)

from src.client.clientA import send_message as sendA
from src.client.clientB import send_message as sendB

PORTS = {"A": 9001, "B": 9100}


class ClientGUI(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.port = PORTS[role]

        self.setWindowTitle(f"Client {role} - SAE 302")
        self.resize(420, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Messages reçus :")
        layout.addWidget(self.label)

        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        layout.addWidget(self.messages)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Entrer un message")
        layout.addWidget(self.input)

        self.btn = QPushButton("Envoyer")
        self.btn.clicked.connect(self.send)
        layout.addWidget(self.btn)

        self.setLayout(layout)

        threading.Thread(target=self.listen, daemon=True).start()

    def send(self):
        msg = self.input.text().strip()
        if not msg:
            return

        if self.role == "A":
            sendA(msg)
        else:
            sendB(msg)

        self.messages.append(f"🟢 Moi : {msg}")
        self.input.clear()

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", self.port))
            s.listen()

            while True:
                conn, _ = s.accept()
                msg = conn.recv(4096).decode()
                conn.close()
                self.messages.append(f"📩 Reçu : {msg}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["A", "B"]:
        print("Usage : python -m src.client.client_gui A|B")
        sys.exit(1)

    app = QApplication(sys.argv)
    gui = ClientGUI(sys.argv[1])
    gui.show()
    sys.exit(app.exec_())
