import os
import time

"""
============================================================
    LANCEUR AUTOMATIQUE DE ROUTEURS (SAE 302)
------------------------------------------------------------
Ce script ouvre plusieurs fenêtres CMD, chacune exécutant
un routeur avec son propre port.

✔ Compatible Windows
✔ Affichage séparé des routeurs
✔ Extensible facilement
============================================================
"""

# --- Liste des routeurs à lancer ---
# Format : ("nom_routeur", port, is_last)
# is_last = True → le routeur envoie la réponse directement à clientB
ROUTERS = [
    ("router1", 8001, False),
    ("router2", 8002, False),
    ("router3", 8003, False),
    ("router4", 8004, False),
    ("router5", 8005, True),   # Le dernier routeur envoie à clientB
]

def launch_router(name, port, is_last):
    """
    Lance un routeur dans une nouvelle fenêtre CMD.
    """

    print(f"Lancement de {name} sur le port {port}...")

    if is_last:
        # Routeur final → envoie directement à clientB
        os.system(f'start cmd /k python -m src.router.router_server {name} 127.0.0.1 {port} clientB')
    else:
        # Routeur normal
        os.system(f'start cmd /k python -m src.router.router_server {name} 127.0.0.1 {port}')

    # Pause pour éviter que les fenêtres ne s’ouvrent toutes en même temps
    time.sleep(0.4)


# ============================================================
#   LANCEMENT DE TOUS LES ROUTEURS
# ============================================================
if __name__ == "__main__":
    print("=== Lancement des routeurs TOR (SAE 302) ===\n")

    for name, port, is_last in ROUTERS:
        launch_router(name, port, is_last)

    print("\n=== Tous les routeurs sont lancés ===")
