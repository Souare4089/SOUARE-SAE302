import random
import sympy

class RSAEncryption:
    """
    RSA pédagogique pour la SAE :
    - p et q en 8 bits pour garantir val < 256
    - Chiffrement par caractère
    - Compatible avec le routage en oignon sans erreurs Unicode
    """

    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.n = None

    # ============================================================
    # GÉNÉRATION DES CLÉS RSA
    # ============================================================
    def generate_keys(self):
        """Génère p, q, n, e, d pour du RSA pédagogique."""

        # ⭐ Correction cruciale : 8 bits → empêche les erreurs chr()
        p = self._generate_prime(8)
        q = self._generate_prime(8)

        self.n = p * q
        phi = (p - 1) * (q - 1)

        # Exposant public classique
        e = 65537
        if self._gcd(e, phi) != 1:
            e = 3

        # Clé privée : inverse modulaire
        d = self._modinv(e, phi)

        self.public_key = (e, self.n)
        self.private_key = (d, self.n)

        return self.public_key, self.private_key

    def _generate_prime(self, bits):
        """Génère un nombre premier de 'bits' bits."""
        while True:
            x = random.getrandbits(bits)
            if sympy.isprime(x):
                return x

    def _gcd(self, a, b):
        """PGCD classique."""
        while b:
            a, b = b, a % b
        return a

    def _modinv(self, a, mod):
        """Inverse modulaire (algorithme d’Euclide étendu)."""
        t, newt = 0, 1
        r, newr = mod, a

        while newr != 0:
            q = r // newr
            t, newt = newt, t - q * newt
            r, newr = newr, r - q * newr

        if r > 1:
            raise Exception("Pas d’inverse modulaire")
        if t < 0:
            t += mod

        return t

    # ============================================================
    # CHIFFREMENT / DÉCHIFFREMENT PAR CARACTÈRE
    # ============================================================
    def encrypt_text(self, text):
        """Chiffre un texte caractère par caractère → liste d'entiers RSA."""
        e, n = self.public_key
        out = []

        for c in text:
            code = ord(c)
            enc = pow(code, e, n)
            out.append(enc)

        return out

    def decrypt_text(self, encrypted_list):
        """Déchiffre une liste d'entiers RSA → texte."""
        d, n = self.private_key
        out = ""

        for enc in encrypted_list:
            code = pow(enc, d, n)

            # ⭐ Garantie : code < 256 → chr() NE plante plus
            out += chr(code)

        return out

    # ============================================================
    #  UTILITAIRES POUR LES TESTS
    # ============================================================
    def encrypt_number(self, number, public_key):
        """Chiffre un entier RSA."""
        e, n = public_key
        return pow(number, e, n)

    def decrypt_number(self, encrypted_number, private_key):
        """Déchiffre un entier RSA."""
        d, n = private_key
        return pow(encrypted_number, d, n)
