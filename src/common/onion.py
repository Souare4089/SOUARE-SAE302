from .crypto import RSAEncryption


class OnionRouter:
    """
    Routage en oignon pédagogique pour la SAE.
    
    VERSION V2 :
    - Les routeurs déchiffrent UNIQUEMENT 1 couche
    - Les routeurs NE convertissent PAS en base64
    - Les couches intermédiaires restent des LISTES d'entiers RSA
    - Seule la couche FINALE vers clientB est du texte clair
    """

    def __init__(self):
        self.crypto = RSAEncryption()

    # ============================================================
    #   CRÉATION DU MESSAGE EN OIGNON (CÔTÉ CLIENT)
    # ============================================================
    def create_onion_message(self, message, destination, router_chain, router_public_keys):
        """
        Construit le message en oignon final :
        
        Pour chaque routeur :
            next_hop|liste_chiffrée
        
        Le premier routeur reçoit la liste chiffrée la plus externe.
        """

        final_payload = f"{destination}|{message}"
        current_layer = None

        # Construction de l'oignon depuis l'intérieur vers l'extérieur
        for router in reversed(router_chain):

            pub_key = router_public_keys[router]

            if current_layer is None:
                # Dernière couche → destination + message
                data = final_payload
            else:
                # Couches intermédiaires → next_router|payload_chiffré
                next_router = router_chain[router_chain.index(router) + 1]
                data = f"{next_router}|{current_layer}"

            # On chiffre data → LISTE d'entiers RSA
            encrypted_list = self._encrypt_layer(data, pub_key)

            # Stockage couche sous forme "1,2,3,4"
            current_layer = ",".join(map(str, encrypted_list))

        return current_layer

    # ============================================================
    #   TRAITEMENT D’UNE COUCHE (CÔTÉ ROUTEUR)
    # ============================================================
    def process_onion_layer(self, encrypted_layer_str, private_key):
        """
        Un routeur reçoit : "12,54,983,12,..."
        Il doit :
            1) Déchiffrer RSA → obtenir "next_hop|payload"
            2) Retourner (next_hop, payload)
        """

        # Convertir "12,54,98" → [12,54,98]
        encrypted_list = [int(x) for x in encrypted_layer_str.split(",")]

        # RSA → texte clair
        decrypted_text = self._decrypt_layer(encrypted_list, private_key)

        # "router4|15,82,123,..." OU "clientB|Bonjour"
        parts = decrypted_text.split("|", 1)

        if len(parts) == 2:
            return parts[0], parts[1]   # next_hop, couche suivante

        # Couche finale → pas de next hop
        return None, decrypted_text

    # ============================================================
    #       CHIFFREMENT INTERNE (RSA → LISTE D’ENTIERS)
    # ============================================================
    def _encrypt_layer(self, text, public_key):
        """
        Chiffre chaque caractère du texte → entier RSA.
        """
        e, n = public_key
        encrypted = []

        for c in text:
            encrypted.append(pow(ord(c), e, n))

        return encrypted

    # ============================================================
    #       DÉCHIFFREMENT INTERNE (RSA → TEXTE)
    # ============================================================
    def _decrypt_layer(self, encrypted_list, private_key):
        """
        Déchiffre une liste RSA → texte clair.
        
        (Cette version ne fait PLUS aucune conversion en base64.)
        """
        d, n = private_key
        out = ""

        for enc in encrypted_list:
            val = pow(enc, d, n)
            out += chr(val)   # OK car payload reste texte ASCII simple

        return out
