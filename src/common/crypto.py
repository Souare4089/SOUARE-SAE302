# Import des modules autorisés
import random
import sympy  # Pour la génération de nombres premiers

class RSAEncryption:
    """Classe pour le chiffrement RSA simplifié"""
    
    def __init__(self):
        # Initialisation des variables pour les clés
        self.public_key = None
        self.private_key = None
        self.n = None  # Module de chiffrement
    
    def generate_keys(self):
        """Génère une paire de clés RSA simplifiée"""
        # Étape 1 : Générer deux nombres premiers
        p = self._generate_prime()
        q = self._generate_prime()
        
        # Calculer n = p * q (module)
        self.n = p * q
        
        # Calculer φ(n) = (p-1)*(q-1)
        phi = (p - 1) * (q - 1)
        
        # Choisir e (exposant public) premier avec φ(n)
        e = self._choose_public_exponent(phi)
        
        # Calculer d (exposant privé) = inverse modulaire de e
        d = self._modular_inverse(e, phi)
        
        # Stocker les clés
        self.public_key = (e, self.n)
        self.private_key = (d, self.n)
        
        print(f"Clés générées - Public: {self.public_key}, Privé: {self.private_key}")
        return self.public_key, self.private_key
    
    def _generate_prime(self):
        """Génère un nombre premier aléatoire"""
        # Génère un nombre premier entre 100 et 1000 (simplifié)
        while True:
            num = random.randint(100, 1000)
            if sympy.isprime(num):
                return num
    
    def _choose_public_exponent(self, phi):
        """Choisit un exposant public premier avec φ(n)"""
        for e in range(3, phi):
            if self._gcd(e, phi) == 1:  # e et phi doivent être premiers entre eux
                return e
        return 65537  # Valeur par défaut
    
    def _gcd(self, a, b):
        """Calcule le plus grand commun diviseur"""
        while b:
            a, b = b, a % b
        return a
    
    def _modular_inverse(self, e, phi):
        """Calcule l'inverse modulaire de e modulo phi"""
        # Algorithme d'Euclide étendu
        t0, t1 = 0, 1
        r0, r1 = phi, e
        
        while r1 != 0:
            quotient = r0 // r1
            t0, t1 = t1, t0 - quotient * t1
            r0, r1 = r1, r0 - quotient * r1
        
        if r0 == 1:
            return t0 % phi
        else:
            raise ValueError("Pas d'inverse modulaire")
    
    def encrypt(self, message, public_key):
        """Chiffre un message avec une clé publique"""
        e, n = public_key
        # Convertit le message en nombre
        message_num = self._text_to_number(message)
        # Chiffre : c = m^e mod n
        encrypted = pow(message_num, e, n)
        return str(encrypted)
    
    def decrypt(self, encrypted_message, private_key):
        """Déchiffre un message avec une clé privée"""
        d, n = private_key
        # Convertit le message chiffré en nombre
        encrypted_num = int(encrypted_message)
        # Déchiffre : m = c^d mod n
        decrypted_num = pow(encrypted_num, d, n)
        # Retourne le texte original
        return self._number_to_text(decrypted_num)
    
    def _text_to_number(self, text):
        """Convertit un texte en nombre"""
        # Conversion simple : chaque caractère -> code ASCII
        number = 0
        for char in text:
            number = number * 256 + ord(char)
        return number
    
    def _number_to_text(self, number):
        """Convertit un nombre en texte"""
        # Conversion inverse
        text = ""
        while number > 0:
            text = chr(number % 256) + text
            number //= 256
        return text