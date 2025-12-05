from .crypto import RSAEncryption

class OnionRouter:
    """
    Routage en oignon pédagogique pour la SAE.
    Chaque couche contient :
    
        next_hop | liste_chiffree
    
    où la liste est une suite d'entiers séparés par des virgules.
    """

    def __init__(self):
        self.crypto = RSAEncryption()

    # ============================================================
    #   CRÉATION DU MESSAGE EN OIGNON (CÔTÉ CLIENT)
    # ============================================================
    def create_onion_message(self, message, destination, router_chain, router_public_keys):
        """
        Construit le message en oignon final qui sera envoyé au premier routeur.

        message : "A"
        destination : "B"
        router_chain : ["router1", "router2", "router3"]
        router_public_keys : dict {"router1": (e,n), ...}

        Retourne : texte contenant la première couche.
        """

        # Dernière couche : destination + message
        final_payload = f"{destination}|{message}"

        # On convertit ce texte en liste RSA chiffrée pour le dernier routeur
        current_layer = None

        # Construction de l’oignon de l'intérieur vers l'extérieur
        for router in reversed(router_chain):

            pub_key = router_public_keys[router]

            # Si aucune couche interne → dernière couche : B|A
            if current_layer is None:
                data = final_payload
            else:
                # data = "next_router|liste_chiffree"
                next_router = router_chain[router_chain.index(router) + 1]
                data = f"{next_router}|{current_layer}"

            # Chiffrement caractère par caractère → liste d'entiers
            encrypted_list = self._encrypt_layer(data, pub_key)

            # On encode la liste sous forme de string : "12,421,54,..."
            current_layer = ",".join(map(str, encrypted_list))

        return current_layer

    # ============================================================
    #   TRAITEMENT D'UNE COUCHE (CÔTÉ ROUTEUR)
    # ============================================================
    def process_onion_layer(self, encrypted_layer_str, private_key):
        """
        Déchiffre UNE couche de l’oignon.

        encrypted_layer_str : "123,456,789"
        private_key : clé RSA du routeur

        Retourne :
            next_hop, remaining_payload
        """

        # Convertir "12,45,8" -> [12,45,8]
        encrypted_list = [int(x) for x in encrypted_layer_str.split(",")]

        # Déchiffrement RSA → texte clair
        decrypted_text = self._decrypt_layer(encrypted_list, private_key)

        # Format attendu : next_hop|payload
        parts = decrypted_text.split("|", 1)

        if len(parts) == 2:
            return parts[0], parts[1]  # next_hop , couche suivante

        # Dernière couche : "B|A"
        return None, decrypted_text

    # ============================================================
    #   OUTILS INTERNE : chiffrement / déchiffrement d'une couche
    # ============================================================
    def _encrypt_layer(self, text, public_key):
        """
        Chiffre un texte caractère par caractère → renvoie une liste d'entiers.
        """
        e, n = public_key
        encrypted = []

        for c in text:
            enc = pow(ord(c), e, n)
            encrypted.append(enc)

        return encrypted

    def _decrypt_layer(self, encrypted_list, private_key):
        """
        Déchiffre la liste d'entiers RSA → reconstitue le texte clair.
        """
        d, n = private_key
        out = ""

        for enc in encrypted_list:
            val = pow(enc, d, n)
            out += chr(val)

        return out
