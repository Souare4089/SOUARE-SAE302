import sys
import mariadb
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton, QTextEdit, QTableWidget,
    QTableWidgetItem
)
from PyQt5.QtCore import QTimer


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "onion_network"
}


class MasterGUI(QWidget):
    """
    Interface graphique du MASTER (SAE 302)
    - Affiche les routeurs enregistrés
    - Affiche les logs
    - Lecture directe depuis MariaDB (cohérent SAE)
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MASTER TOR - SAE 302")
        self.setGeometry(200, 200, 700, 500)

        self.layout = QVBoxLayout()

        self.label = QLabel("📡 Routeurs enregistrés")
        self.layout.addWidget(self.label)

        # Tableau des routeurs
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nom", "IP", "Port", "Clé publique (e,n)"])
        self.layout.addWidget(self.table)

        # Logs
        self.log_label = QLabel("📝 Logs")
        self.layout.addWidget(self.log_label)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.layout.addWidget(self.logs)

        # Bouton refresh
        self.refresh_btn = QPushButton("🔄 Rafraîchir")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.layout.addWidget(self.refresh_btn)

        self.setLayout(self.layout)

        # Timer auto-refresh (toutes les 3 secondes)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(3000)

        self.refresh_data()

    # ======================================================
    # Connexion BDD
    # ======================================================
    def get_connection(self):
        return mariadb.connect(**DB_CONFIG)

    # ======================================================
    # Rafraîchissement
    # ======================================================
    def refresh_data(self):
        self.load_routers()
        self.load_logs()

    # ======================================================
    # Routeurs
    # ======================================================
    def load_routers(self):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT name, ip, port, public_e, public_n FROM routers")
            rows = cur.fetchall()

            self.table.setRowCount(len(rows))

            for i, row in enumerate(rows):
                self.table.setItem(i, 0, QTableWidgetItem(row[0]))
                self.table.setItem(i, 1, QTableWidgetItem(row[1]))
                self.table.setItem(i, 2, QTableWidgetItem(str(row[2])))
                self.table.setItem(
                    i, 3,
                    QTableWidgetItem(f"({row[3]}, {row[4]})")
                )

            cur.close()
            conn.close()

        except Exception as e:
            self.logs.append(f"❌ Erreur routeurs : {e}")

    # ======================================================
    # Logs
    # ======================================================
    def load_logs(self):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT message, timestamp FROM logs ORDER BY id DESC LIMIT 20")
            rows = cur.fetchall()

            self.logs.clear()
            for msg, ts in rows:
                self.logs.append(f"[{ts}] {msg}")

            cur.close()
            conn.close()

        except Exception as e:
            self.logs.append(f"❌ Erreur logs : {e}")


# ======================================================
# Lancement
# ======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = MasterGUI()
    gui.show()
    sys.exit(app.exec_())
