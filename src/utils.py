"""
utils.py
--------
Shared utility functions: logging, image I/O, progress display,
file sizing helpers, and preview generation for encrypted data.
"""

import io
import os
import datetime
import textwrap
import numpy as np
from PIL import Image

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────

LOG_FILE = "transmission_log.txt"


def log(message: str, level: str = "INFO") -> None:
    """
    Append a timestamped log entry to LOG_FILE and print to stdout.

    Args:
        message: Human-readable description of the event
        level:   Severity tag – INFO | WARNING | ERROR | SUCCESS
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry     = f"[{timestamp}] [{level}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


def clear_log() -> None:
    """Wipe the log file at the start of a new session."""
    with open(LOG_FILE, "w") as f:
        f.write(f"=== Secure Space Image Transmission Log ===\n")
        f.write(f"Session started: {datetime.datetime.now()}\n\n")


# ─────────────────────────────────────────────
# Image helpers
# ─────────────────────────────────────────────

def load_image_bytes(path: str) -> bytes:
    """
    Read a JPG/PNG from disk and return its raw byte content.

    Args:
        path: Absolute or relative file path

    Returns:
        Raw file bytes
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    with open(path, "rb") as f:
        return f.read()


def bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """
    Convert raw image bytes to a PIL Image object.

    Args:
        image_bytes: Raw JPG/PNG bytes

    Returns:
        PIL Image
    """
    return Image.open(io.BytesIO(image_bytes))


def save_image_bytes(image_bytes: bytes, path: str) -> None:
    """
    Write raw image bytes to a file.

    Args:
        image_bytes: Raw JPG/PNG bytes
        path:        Destination file path
    """
    with open(path, "wb") as f:
        f.write(image_bytes)


# ─────────────────────────────────────────────
# Encrypted data preview
# ─────────────────────────────────────────────

def encrypted_preview_array(encrypted_bytes: bytes, height: int = 128, width: int = 256) -> np.ndarray:
    """
    Reshape encrypted bytes into a 2-D grayscale array for visualization.
    Pads or truncates to fit the requested dimensions.

    Args:
        encrypted_bytes: Raw cipher-text
        height, width:   Preview image dimensions in pixels

    Returns:
        NumPy uint8 array of shape (height, width)
    """
    needed = height * width
    raw    = np.frombuffer(encrypted_bytes[:needed], dtype=np.uint8)

    # Pad with zeros if the encrypted payload is shorter than the canvas
    if len(raw) < needed:
        raw = np.pad(raw, (0, needed - len(raw)))

    return raw.reshape((height, width))


# ─────────────────────────────────────────────
# File-size helpers
# ─────────────────────────────────────────────

def human_size(num_bytes: int) -> str:
    """
    Format a byte count as a human-readable string (KB / MB).

    Args:
        num_bytes: Size in bytes

    Returns:
        Formatted string, e.g. "142.3 KB"
    """
    if num_bytes < 1024:
        return f"{num_bytes} B"
    elif num_bytes < 1024 ** 2:
        return f"{num_bytes / 1024:.1f} KB"
    else:
        return f"{num_bytes / 1024**2:.2f} MB"


def size_comparison(original_bytes: bytes, encrypted_bytes: bytes) -> dict:
    """
    Build a size-comparison summary dict.

    Returns dict with keys: original, encrypted, overhead_pct
    """
    orig = len(original_bytes)
    enc  = len(encrypted_bytes)
    return {
        "original":     human_size(orig),
        "encrypted":    human_size(enc),
        "overhead_pct": round((enc - orig) / orig * 100, 2),
    }


# ─────────────────────────────────────────────
# Progress indicator (text-based)
# ─────────────────────────────────────────────

def progress_bar(label: str, steps: int = 20, char: str = "█") -> None:
    """
    Print an animated text progress bar to stdout.

    Args:
        label: Text to show beside the bar
        steps: Number of fill increments
        char:  Fill character
    """
    import sys
    bar = ""
    for i in range(steps + 1):
        bar = char * i + "░" * (steps - i)
        pct = int(i / steps * 100)
        sys.stdout.write(f"\r  {label}: [{bar}] {pct}%")
        sys.stdout.flush()
        import time; time.sleep(0.03)
    print()   # newline after completion
