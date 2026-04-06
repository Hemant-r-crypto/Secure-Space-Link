"""
decryption.py
-------------
Handles AES decryption of received encrypted image data.
Reverses the encryption process to reconstruct original image bytes.
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt_image(encrypted_bytes: bytes, key: bytes, iv: bytes) -> bytes:
    """
    Decrypt AES-CBC cipher-text and remove PKCS7 padding.

    Args:
        encrypted_bytes: Cipher-text received after transmission
        key:             32-byte AES key (must match encryption key)
        iv:              16-byte IV (must match encryption IV)

    Returns:
        original_bytes (bytes): Reconstructed raw image bytes

    Raises:
        ValueError: If decryption fails due to bad key/IV or tampered data
    """
    try:
        cipher         = AES.new(key, AES.MODE_CBC, iv)
        decrypted_raw  = cipher.decrypt(encrypted_bytes)
        original_bytes = unpad(decrypted_raw, AES.block_size)
        return original_bytes
    except (ValueError, KeyError) as exc:
        raise ValueError(f"Decryption failed — data may be corrupted or tampered: {exc}") from exc


def load_encrypted_file(path: str) -> bytes:
    """
    Load encrypted bytes from a .bin file on disk.

    Args:
        path: File path to the encrypted binary file

    Returns:
        bytes: Raw encrypted content
    """
    with open(path, "rb") as f:
        return f.read()
