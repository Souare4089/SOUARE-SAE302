import os
import time
import platform

"""
============================================================
    LANCEUR AUTOMATIQUE DE ROUTEURS (SAE 302)
------------------------------------------------------------
✔ Compatible Windows ET Linux
✔ Lance tous les routeurs automatiquement
✔ Chaque routeur a son port
✔ Le dernier routeur envoie vers clientB
============================================================
"""

# ------------------------------------------------------------
# Liste des routeurs
# Format : (nom, port, is_last)
# ------------------------------------------------------------
ROUTERS = [
    ("router1", 8001, False),
    ("router2", 8002, False),
    ("router3", 8003, False),
    ("router4", 8004, False),
    ("router5", 8005, True),   # dernier routeur → clientB
]

IS_WINDOWS = platform.system().lower().startswith("win")


def launch_router(name, port, is_last):
    print(f"Lancement de {name} sur le port {port}...")

    if IS_WINDOWS:
        # =========================
        # WINDOWS
        # =========================
        if is_last:
            os.system(
                f'start cmd /k python -m src.router.router_server {name} 127.0.0.1 {port} clientB'
            )
        else:
            os.system(
                f'start cmd /k python -m src.router.router_server {name} 127.0.0.1 {port}'
            )
    else:
        # =========================
        # LINUX
        # =========================
        if is_last:
            os.system(
                f'python3 -m src.router.router_server {name} 0.0.0.0 {port} clientB &'
            )
        else:
            os.system(
                f'python3 -m src.router.router_server {name} 0.0.0.0 {port} &'
            )

    # Pause pour éviter les conflits
    time.sleep(0.4)


# ============================================================
# LANCEMENT GLOBAL
# ============================================================
if __name__ == "__main__":
    print("=== Lancement des routeurs TOR (SAE 302) ===\n")

    for name, port, is_last in ROUTERS:
        launch_router(name, port, is_last)

    print("\n=== Tous les routeurs sont lancés ===")
