# SAE 3.02 - Développer des applications communicantes

Étudiant : Ibrahima SOUARE
BUT Réseaux et Télécommunications - Parcours DevCloud
IUT de Colmar - Année 2025-2026

## Présentation du projet

Conception et implémentation d'un système de communication anonyme inspiré du réseau TOR. Chaque message passe par plusieurs routeurs virtuels sans qu'on puisse identifier l'origine. Projet réalisé seul, de la conception au déploiement.

## Ce que j'ai réalisé

- Serveur Master centralisant les routeurs et distribuant les clés
- Routeurs virtuels effectuant un routage multi-sauts avec déchiffrement par couche
- Clients bidirectionnels avec interface graphique PyQt
- Chiffrement asymétrique RSA par couches
- Base de données MariaDB pour stocker les clés et les routes
- Déploiement sur 3 machines virtuelles : 1 VM Linux Master, 1 VM Linux Routeurs, 1 VM Windows Clients

## Technologies utilisées

Python, Sockets TCP, Threading, PyQt5, MariaDB, Chiffrement RSA, VirtualBox, Git

## Installation

Voir le fichier SAE302_Installation_et_Utilisation.md pour les instructions complètes.
