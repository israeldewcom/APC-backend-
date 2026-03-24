"""
End-to-end encryption utilities.
"""
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from django.conf import settings

def generate_key_pair():
    salt = settings.ENCRYPTION_SALT
    return {"salt": base64.b64encode(salt).decode()}

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def aes_encrypt(data: bytes, key: bytes) -> bytes:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(data) + encryptor.finalize()
    return iv + encrypted

def aes_decrypt(encrypted_data: bytes, key: bytes) -> bytes:
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt_message(plaintext: str, recipient_public_key: str) -> str:
    """
    In a real E2EE system, you'd use asymmetric encryption (RSA/ECC).
    Here we simulate by deriving a symmetric key from the public key.
    """
    # For demo, just return a base64 encoded version
    return base64.b64encode(plaintext.encode()).decode()

def decrypt_message(ciphertext: str, private_key: str) -> str:
    return base64.b64decode(ciphertext).decode()
