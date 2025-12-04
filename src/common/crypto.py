# Import des modules autorisés
import random
import sympy  # Pour la génération de nombres premiers

class RSAEncryption:
    """Classe pour le chiffrement RSA simplifié utilisé dans le routage en oignon."""
    
    def __init__(self):
        # Les clés seront stockées dans ces variables
        self.public_key = None
        self.private_key = None
        self.n = None  # Module commun aux clés publique/privée
    
    def generate_keys(self):
        """
        Génère une paire de clés RSA simplifiée.
        Cette version utilise des entiers plus grands (512 bits) pour éviter 
        que le message soit plus grand que n.
        """

        # Étape 1 : générer deux grands nombres premiers p et q
        p = self._generate_prime(256)  # Premier de 256 bits
        q = self._generate_prime(256)  # Premier de 256 bits

        # Étape 2 : calcul du module n = p * q
        self.n = p * q

        # Étape 3 : calcul de φ(n) = (p-1)(q-1)
        phi = (p - 1) * (q - 1)

        # Étape 4 : choisir un exposant public e premier avec φ(n)
        e = self._choose_public_exponent(phi)

        # Étape 5 : calcul de d, l'inverse modulaire de e
        d = self._modular_inverse(e, phi)

        # Stockage des clés
        self.public_key = (e, self.n)
        self.private_key = (d, self.n)

        return self.public_key, self.private_key
    
    def _generate_prime(self, bits):
        """
        Génère un nombre premier de taille 'bits' bits.
        On utilise sympy.isprime pour la validation.
        """
        while True:
            num = random.getrandbits(bits)
            if sympy.isprime(num):
                return num
    
    def _choose_public_exponent(self, phi):
        """
        Choisit un exposant public e.
        On utilise la valeur standard 65537 qui est :
        - sûre
        - très utilisée dans RSA
        - rapide
        - première avec la majorité des phi(n)
        """
        if self._gcd(65537, phi) == 1:
            return 65537
        
        # Sinon, on parcourt pour trouver un e valide
        for e in range(3, phi):
            if self._gcd(e, phi) == 1:
                return e
        
        raise ValueError("Impossible de trouver un exposant public valide.")

    def _gcd(self, a, b):
        """Calcule le PGCD avec l'algorithme d'Euclide."""
        while b:
            a, b = b, a % b
        return a
    
    def _modular_inverse(self, e, phi):
        """Calcule d dans : d * e ≡ 1 (mod φ(n)) grâce à l'algorithme d'Euclide étendu."""
        t0, t1 = 0, 1
        r0, r1 = phi, e
        
        while r1 != 0:
            quotient = r0 // r1
            t0, t1 = t1, t0 - quotient * t1
            r0, r1 = r1, r0 - quotient * r1
        
        if r0 == 1:
            return t0 % phi
        else:
            raise ValueError("Pas d'inverse modulaire trouvé.")
    
    def encrypt(self, message, public_key):
        """
        Chiffre un message texte en utilisant RSA.
        Convertit d'abord le texte en nombre puis applique m^e mod n.
        """
        e, n = public_key

        message_num = self._text_to_number(message)

        # Vérification : le message ne doit jamais être >= n
        if message_num >= n:
            raise ValueError("Message trop long pour être chiffré en un seul bloc RSA.")

        encrypted = pow(message_num, e, n)
        return str(encrypted)
    
    def decrypt(self, encrypted_message, private_key):
        """
        Déchiffre un message RSA et renvoie le texte original.
        """
        d, n = private_key
        encrypted_num = int(encrypted_message)
        decrypted_num = pow(encrypted_num, d, n)
        return self._number_to_text(decrypted_num)
    
    def encrypt_number(self, number, public_key):
        """Chiffre un entier (utile pour les routeurs et hops)."""
        e, n = public_key
        return pow(number, e, n)
    
    def decrypt_number(self, encrypted_number, private_key):
        """Déchiffre un entier RSA."""
        d, n = private_key
        return pow(encrypted_number, d, n)
    
    def _text_to_number(self, text):
        """
        Convertit un texte en nombre entier.
        Procédé : concaténation des codes ASCII (base 256).
        """
        number = 0
        for char in text:
            number = number * 256 + ord(char)
        return number
    
    def _number_to_text(self, number):
        """
        Convertit un nombre entier en texte (inverse de text_to_number).
        """
        text = ""
        while number > 0:
            text = chr(number % 256) + text
            number //= 256
        return text
