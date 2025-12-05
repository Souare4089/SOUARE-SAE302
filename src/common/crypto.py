import random
import sympy

class RSAEncryption:
    """
    RSA pédagogique pour la SAE :
    - Génération de clés correcte
    - Chiffrement caractère par caractère
    - Liste d'entiers en sortie → parfait pour le routage en oignon
    """

    def __init__(self):
        self.public_key = None
        self.private_key = None
        self.n = None

    # ============================================================
    # GÉNÉRATION DES CLÉS
    # ============================================================
    def generate_keys(self):
        """Génère p, q, n, e, d pour du RSA pédagogique."""

        p = self._generate_prime(16)   # 16 bits = assez petit pour la SAE
        q = self._generate_prime(16)

        self.n = p * q
        phi = (p - 1) * (q - 1)

        e = 65537
        if self._gcd(e, phi) != 1:
            e = 3

        d = self._modinv(e, phi)

        self.public_key = (e, self.n)
        self.private_key = (d, self.n)

        return self.public_key, self.private_key

    def _generate_prime(self, bits):
        while True:
            x = random.getrandbits(bits)
            if sympy.isprime(x):
                return x

    def _gcd(self, a, b):
        while b:
            a, b = b, a % b
        return a

    def _modinv(self, a, mod):
        """Inverse modulaire (Euclide étendu)."""
        t, newt = 0, 1
        r, newr = mod, a

        while newr != 0:
            q = r // newr
            t, newt = newt, t - q * newt
            r, newr = newr, r - q * newr

        if r > 1:
            raise Exception("Pas inversible")
        if t < 0:
            t += mod

        return t

    # ============================================================
    # CHIFFREMENT PAR CARACTÈRE
    # ============================================================
    def encrypt_text(self, text):
        """Renvoie une liste d'entiers RSA."""
        e, n = self.public_key
        out = []

        for c in text:
            code = ord(c)         # ASCII
            enc = pow(code, e, n) # RSA(c)
            out.append(enc)

        return out

    def decrypt_text(self, encrypted_list):
        """Reconstitue le texte depuis la liste RSA."""
        d, n = self.private_key
        out = ""

        for enc in encrypted_list:
            code = pow(enc, d, n) # RSA^-1
            out += chr(code)

        return out

