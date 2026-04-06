"""
encryption.py
-------------
Handles AES encryption of image data using AES-CBC mode.
Generates a random AES-256 key and IV for each session.
"""

import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def generate_key_iv():
    """
    Generate a random 256-bit AES key and 128-bit IV.

    Returns:
        key (bytes): 32-byte AES key
        iv  (bytes): 16-byte initialization vector
    """
    key = os.urandom(32)   # AES-256
    iv  = os.urandom(16)   # AES block size
    return key, iv


def encrypt_image(image_bytes: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Encrypt raw image bytes with AES-CBC and PKCS7 padding.

    Args:
        image_bytes: Raw bytes of the image file
        key:         32-byte AES key
        iv:          16-byte IV

    Returns:
        encrypted (bytes): Padded, encrypted cipher-text
    """
    cipher    = AES.new(key, AES.MODE_CBC, iv)
    padded    = pad(image_bytes, AES.block_size)
    encrypted = cipher.encrypt(padded)
    return encrypted


def save_encrypted_file(encrypted_bytes: bytes, path: str) -> None:
    """
    Persist encrypted bytes to a .bin file.

    Args:
        encrypted_bytes: Cipher-text to write
        path:            Destination file path (should end in .bin)
    """
    with open(path, "wb") as f:
        f.write(encrypted_bytes)
