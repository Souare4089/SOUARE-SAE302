import mariadb
import sys


class DatabaseManager:
    """
    Classe permettant de gérer toutes les opérations avec MariaDB.
    Utilisée par le Master.
    """

    def __init__(self, host="localhost", user="root", password="1234", database="onion_network"):

        self.host = host
        self.user = user
        self.password = password
        self.database = database

        # Connexion sans base pour la créer si besoin
        try:
            self.conn = mariadb.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
        except mariadb.Error as e:
            print(f"[ERREUR] Connexion MariaDB impossible : {e}")
            sys.exit(1)

        self._create_database()

        # Reconnexion avec la base sélectionnée
        try:
            self.conn = mariadb.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
        except mariadb.Error as e:
            print(f"[ERREUR] Sélection de la base impossible : {e}")
            sys.exit(1)

        self._create_tables()

    # ============================================================
    # CRÉATION BASE + TABLES
    # ============================================================
    def _create_database(self):
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        except mariadb.Error as e:
            print(f"[ERREUR] Création base impossible : {e}")
            sys.exit(1)

    def _create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS routers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50),
                    ip VARCHAR(50),
                    port INT,
                    public_e LONGTEXT,
                    public_n LONGTEXT
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except mariadb.Error as e:
            print(f"[ERREUR] Création tables impossible : {e}")

    # ============================================================
    # ROUTEURS
    # ============================================================
    def remove_router(self, name):
        """
        Supprime toutes les entrées d'un routeur par son nom.
        Utilisé pour éviter les doublons.
        """
        try:
            self.cursor.execute("DELETE FROM routers WHERE name = ?", (name,))
            self.conn.commit()
        except mariadb.Error as e:
            print(f"[ERREUR] Suppression routeur impossible : {e}")

    def add_router(self, name, ip, port, public_key):
        """
        Ajoute un routeur dans la base.
        public_key = (e, n)
        """
        e, n = public_key
        try:
            self.cursor.execute(
                "INSERT INTO routers (name, ip, port, public_e, public_n) VALUES (?, ?, ?, ?, ?)",
                (name, ip, port, str(e), str(n))
            )
            self.conn.commit()
            print(f"[DB] Routeur {name} ajouté.")
        except mariadb.Error as e:
            print(f"[ERREUR] Ajout routeur impossible : {e}")

    def get_routers(self):
        """
        Retourne la liste des routeurs.
        """
        try:
            self.cursor.execute("SELECT name, ip, port, public_e, public_n FROM routers")
            rows = self.cursor.fetchall()

            routers = []
            for row in rows:
                routers.append({
                    "name": row[0],
                    "ip": row[1],
                    "port": row[2],
                    "public_key": (int(row[3]), int(row[4]))
                })

            return routers

        except mariadb.Error as e:
            print(f"[ERREUR] Récupération routeurs impossible : {e}")
            return []

    # ============================================================
    # LOGS
    # ============================================================
    def add_log(self, message):
        try:
            self.cursor.execute("INSERT INTO logs (message) VALUES (?)", (message,))
            self.conn.commit()
        except mariadb.Error as e:
            print(f"[ERREUR] Ajout log impossible : {e}")

    def close(self):
        self.cursor.close()
        self.conn.close()
