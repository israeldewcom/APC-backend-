"""
Helper functions for end-to-end encryption (E2EE).
Handles key generation, encryption/decryption using client-side keys.
"""
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
from django.conf import settings

def generate_key_pair():
    """
    In a real E2EE system, this would generate a public/private key pair.
    But since encryption happens client-side, we just provide the salt.
    """
    salt = settings.ENCRYPTION_SALT
    return {"salt": base64.b64encode(salt).decode()}

def encrypt_message(plaintext, recipient_public_key):
    """
    Placeholder: Actual encryption happens on client.
    This function is for server-side key management.
    """
    pass

def decrypt_message(ciphertext, private_key):
    pass

def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a symmetric key from password using PBKDF2."""
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
