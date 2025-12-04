import mariadb
import sys

class DatabaseManager:
    """
    Classe permettant de gérer toutes les opérations avec MariaDB.
    Elle sera utilisée par le Master et éventuellement les routeurs.
    """

    def __init__(self, host="localhost", user="root", password="", database="onion_network"):
        """
        Initialise la connexion à la base MariaDB.
        Si la base n'existe pas encore, elle est créée automatiquement.
        """

        self.host = host
        self.user = user
        self.password = password
        self.database = database

        # D'abord essayer de se connecter à MariaDB sans sélectionner de base
        try:
            self.conn = mariadb.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor()
        except mariadb.Error as e:
            print(f"[ERREUR] Impossible de se connecter à MariaDB : {e}")
            sys.exit(1)

        # Créer la base si elle n'existe pas
        self._create_database()

        # Se reconnecter mais cette fois-ci dans la bonne base
        try:
            self.conn = mariadb.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
        except mariadb.Error as e:
            print(f"[ERREUR] Impossible de sélectionner la base {self.database} : {e}")
            sys.exit(1)

        # Créer les tables nécessaires
        self._create_tables()

    def _create_database(self):
        """Crée la base si elle n'existe pas."""
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        except mariadb.Error as e:
            print(f"[ERREUR] Impossible de créer la base {self.database} : {e}")
            sys.exit(1)

    def _create_tables(self):
        """Crée les tables nécessaires au projet."""
        queries = [

            # Table des routeurs
            """
            CREATE TABLE IF NOT EXISTS routers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50),
                ip VARCHAR(50),
                port INT,
                public_e LONGTEXT,
                public_n LONGTEXT
            )
            """,

            # Table des logs
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]

        for query in queries:
            try:
                self.cursor.execute(query)
            except mariadb.Error as e:
                print(f"[ERREUR] Impossible de créer une table : {e}")

    def add_router(self, name, ip, port, public_key):
        """
        Ajoute un routeur dans la base avec sa clé publique.
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
            print(f"[ERREUR] Impossible d'ajouter un routeur : {e}")

    def get_routers(self):
        """
        Récupère la liste des routeurs sous forme de dictionnaires.
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
            print(f"[ERREUR] Impossible de récupérer les routeurs : {e}")
            return []

    def add_log(self, message):
        """
        Ajoute un log dans la base.
        Utile pour le Master (suivi du réseau).
        """
        try:
            self.cursor.execute("INSERT INTO logs (message) VALUES (?)", (message,))
            self.conn.commit()
        except mariadb.Error as e:
            print(f"[ERREUR] Impossible d'ajouter un log : {e}")

    def close(self):
        """Ferme proprement la connexion."""
        self.cursor.close()
        self.conn.close()
