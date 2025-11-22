# Import du connecteur MySQL pour MariaDB
import mysql.connector

class Database:
    def __init__(self):
        # Initialisation de la connexion à None (non connecté)
        self.connection = None
    
    def connect(self):
        """Établit la connexion à la base de données MariaDB"""
        try:
            # Tentative de connexion à la base de données
            self.connection = mysql.connector.connect(
                host="localhost",      # Serveur local
                user="root",           # Utilisateur par défaut
                password="1234",  # MOT DE PASSE À MODIFIER
                database="onion_router" # Nom de la base de données
            )
            print("Connexion à la base de données réussie")
            return self.connection
        except mysql.connector.Error as err:
            # Gestion des erreurs de connexion
            print(f"Erreur de connexion: {err}")
            return None

    def create_database(self):
        """Crée la base de données et les tables si elles n'existent pas"""
        try:
            # Connexion temporaire sans base de données spécifiée
            temp_conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234"  # MOT DE PASSE À MODIFIER
            )
            cursor = temp_conn.cursor()
            
            # Création de la base de données si elle n'existe pas
            cursor.execute("CREATE DATABASE IF NOT EXISTS onion_router")
            print("Base de données 'onion_router' créée ou déjà existante")
            
            # Sélection de la base de données
            cursor.execute("USE onion_router")
            
            # Création de la table pour stocker les clés des routeurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS keys_table (
                    router_id VARCHAR(50) PRIMARY KEY,
                    public_key TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Table 'keys_table' créée ou déjà existante")
            
            # Fermeture du curseur et de la connexion temporaire
            cursor.close()
            temp_conn.close()
            return True
            
        except mysql.connector.Error as err:
            # Gestion des erreurs lors de la création
            print(f"Erreur création base: {err}")
            return False