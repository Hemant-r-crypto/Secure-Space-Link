"""
integrity.py
------------
SHA-256 based data integrity verification.
Generates a hash before transmission and validates it after reception.
"""

import hashlib


def compute_sha256(data: bytes) -> str:
    """
    Compute the SHA-256 hex digest of arbitrary bytes.

    Args:
        data: Byte sequence to hash (encrypted image payload)

    Returns:
        hex_digest (str): 64-character lowercase hex string
    """
    return hashlib.sha256(data).hexdigest()


def verify_integrity(original_hash: str, received_data: bytes) -> tuple[bool, str]:
    """
    Re-hash received data and compare against the original hash.

    Args:
        original_hash: SHA-256 digest computed before transmission
        received_data: Bytes received at the ground station

    Returns:
        (is_intact, received_hash) tuple:
            is_intact     – True if hashes match, False if data was altered
            received_hash – SHA-256 digest of the received data
    """
    received_hash = compute_sha256(received_data)
    is_intact     = (original_hash == received_hash)
    return is_intact, received_hash
