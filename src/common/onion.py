# Import des modules nécessaires
from .crypto import RSAEncryption

class OnionRouter:
    """Gère le routage en oignon avec chiffrement par couches"""
    
    def __init__(self):
        self.crypto = RSAEncryption()
    
    def create_onion_message(self, message, destination, router_chain, router_public_keys):
        """
        Crée un message en oignon avec plusieurs couches de chiffrement
        
        Args:
            message: le message à envoyer
            destination: le client destinataire
            router_chain: liste des routeurs [R1, R2, R3]
            router_public_keys: dictionnaire {routeur: clé_publique}
        """
        # Commencer par la dernière couche (destination + message)
        current_payload = f"{destination}|{message}"
        print(f"Payload initial: {current_payload}")
        
        # Convertir en nombre pour le chiffrement
        current_payload_num = self._text_to_number(current_payload)
        print(f"Payload en nombre: {current_payload_num}")
        
        # Parcourir les routeurs à l'envers (de R3 à R1)
        for router in reversed(router_chain):
            # Récupérer la clé publique du routeur
            public_key = router_public_keys[router]
            
            # Créer la charge utile pour ce routeur
            if router != router_chain[-1]:  # Pas le dernier routeur
                next_router = router_chain[router_chain.index(router) + 1]
                payload_text = f"{next_router}|{self._number_to_text(current_payload_num)}"
            else:  # Dernier routeur
                payload_text = self._number_to_text(current_payload_num)
            
            # Convertir en nombre et chiffrer
            payload_num = self._text_to_number(payload_text)
            current_payload_num = self.crypto.encrypt_number(payload_num, public_key)
            print(f"Couche {router} chiffrée: {current_payload_num}")
        
        return str(current_payload_num)
    
    def process_onion_layer(self, encrypted_layer, private_key):
        """
        Traite une couche d'oignon (déchiffre et extrait le prochain saut)
        
        Args:
            encrypted_layer: la couche chiffrée reçue
            private_key: clé privée du routeur pour déchiffrer
        
        Returns:
            tuple: (next_hop, remaining_payload) ou (destination, message)
        """
        # Vérifier si encrypted_layer est déjà un nombre ou du texte
        if isinstance(encrypted_layer, str) and encrypted_layer.isdigit():
            encrypted_num = int(encrypted_layer)
        else:
            # Si c'est du texte, le convertir en nombre
            encrypted_num = self._text_to_number(encrypted_layer)
        
        decrypted_num = self.crypto.decrypt_number(encrypted_num, private_key)
        decrypted_text = self._number_to_text(decrypted_num)
        
        print(f"Couche déchiffrée: {decrypted_text}")
        
        # Séparer le prochain saut du reste du payload
        parts = decrypted_text.split('|', 1)
        
        if len(parts) == 2:
            next_hop, remaining_payload = parts
            return next_hop, remaining_payload
        else:
            # Dernière couche : destination + message
            return None, decrypted_text
    
    def _text_to_number(self, text):
        """Convertit un texte en nombre"""
        number = 0
        for char in text:
            number = number * 256 + ord(char)
        return number
    
    def _number_to_text(self, number):
        """Convertit un nombre en texte"""
        text = ""
        while number > 0:
            text = chr(number % 256) + text
            number //= 256
        return text