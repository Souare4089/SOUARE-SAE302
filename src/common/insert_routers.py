from src.common.database import DatabaseManager
from src.router.router_server import RouterServer

# Connexion à la base
db = DatabaseManager(password="1234")

# Nombre de routeurs à créer
N = 5   # Tu peux mettre 3, 5, 10...

print(f"[SETUP] Ajout de {N} routeurs dans la base...")

for i in range(1, N + 1):
    name = f"router{i}"
    ip = "127.0.0.1"
    port = 8000 + i   # router1 → 8001, router2 → 8002, etc.

    # Création d’un routeur temporaire juste pour générer sa clé publique
    router = RouterServer(name, ip, port)

    # Ajout à la base
    db.add_router(name, ip, port, router.public_key)

print("[SETUP] Routeurs ajoutés avec succès !")
