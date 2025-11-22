import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Souare.4089!"  # Essaye sans mot de passe si vide
    )
    print("✅ Connexion réussie")
    conn.close()
except Exception as e:
    print(f"❌ Erreur: {e}")