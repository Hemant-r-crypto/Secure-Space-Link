"""
main.py
-------
Secure Space Image Transmission System
=======================================
Orchestrates the full pipeline:
  1. Image upload / load
  2. AES-256 encryption
  3. Simulated transmission (with optional attacks)
  4. SHA-256 integrity check
  5. AES decryption
  6. Visual dashboard (matplotlib)
  7. Logging

Run in Google Colab:
    !python main.py
Or step-through the pipeline interactively (see bottom of file).
"""

import os
import sys
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from PIL import Image

# ── Local modules ──────────────────────────────────────────────────────────────
from encryption   import generate_key_iv, encrypt_image, save_encrypted_file
from decryption   import decrypt_image, load_encrypted_file
from integrity    import compute_sha256, verify_integrity
from transmission import transmit
from utils        import (
    log, clear_log,
    load_image_bytes, bytes_to_pil, save_image_bytes,
    encrypted_preview_array, size_comparison, human_size,
    progress_bar,
)

# ── Constants ──────────────────────────────────────────────────────────────────
ENCRYPTED_PATH  = "encrypted_image.bin"
DECRYPTED_PATH  = "decrypted_image.png"


# ══════════════════════════════════════════════════════════════════════════════
# Helper: Colab file upload
# ══════════════════════════════════════════════════════════════════════════════

def upload_image_colab() -> str:
    """
    Trigger Google Colab's file-upload widget.
    Returns the path to the first uploaded file.
    """
    try:
        from google.colab import files
        uploaded = files.upload()
        if not uploaded:
            raise ValueError("No file was uploaded.")
        filename = list(uploaded.keys())[0]
        log(f"File uploaded via Colab widget: {filename}")
        return filename
    except ImportError:
        # Fallback: ask for a local path (useful when running outside Colab)
        path = input("Enter the path to your image file: ").strip()
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        return path


# ══════════════════════════════════════════════════════════════════════════════
# Pipeline stages
# ══════════════════════════════════════════════════════════════════════════════

def stage_encrypt(image_path: str):
    """
    Stage 1 – Encrypt the source image.

    Returns:
        image_bytes     (bytes)  – original raw image bytes
        encrypted_bytes (bytes)  – AES cipher-text
        key             (bytes)  – 32-byte AES key
        iv              (bytes)  – 16-byte AES IV
        original_hash   (str)    – SHA-256 of cipher-text before transmission
    """
    print("\n" + "═"*60)
    print("  🛰️  STAGE 1 – ENCRYPTION")
    print("═"*60)

    progress_bar("Loading image   ", steps=10)
    image_bytes = load_image_bytes(image_path)
    log(f"Image loaded: {image_path} ({human_size(len(image_bytes))})")

    progress_bar("Generating keys ", steps=10)
    key, iv = generate_key_iv()
    log("AES-256 key and IV generated.")

    progress_bar("Encrypting      ", steps=20)
    encrypted_bytes = encrypt_image(image_bytes, key, iv)
    save_encrypted_file(encrypted_bytes, ENCRYPTED_PATH)
    log(f"Encryption complete → {ENCRYPTED_PATH} ({human_size(len(encrypted_bytes))})", "SUCCESS")

    # Size report
    sizes = size_comparison(image_bytes, encrypted_bytes)
    print(f"\n  📦 Original : {sizes['original']}")
    print(f"  🔒 Encrypted: {sizes['encrypted']}  (overhead +{sizes['overhead_pct']}%)")

    # Hash payload BEFORE transmission
    original_hash = compute_sha256(encrypted_bytes)
    log(f"Pre-transmission SHA-256: {original_hash[:16]}…")

    return image_bytes, encrypted_bytes, key, iv, original_hash


def stage_transmit(encrypted_bytes: bytes, attack: str = "none"):
    """
    Stage 2 – Simulate transmission over an insecure channel.

    Args:
        encrypted_bytes: Cipher-text to send
        attack:          "none" | "tamper" | "noise"

    Returns:
        received_bytes (bytes): What the ground station receives
        meta           (dict):  Transmission metadata
    """
    print("\n" + "═"*60)
    print("  📡  STAGE 2 – TRANSMISSION")
    print("═"*60)

    if attack != "none":
        print(f"\n  ⚠️  Attack mode enabled: [{attack.upper()}]")
        log(f"Attack simulation enabled: {attack}", "WARNING")

    progress_bar("Transmitting    ", steps=25)
    received_bytes, meta = transmit(encrypted_bytes, attack=attack, latency_ms=400)

    print(f"\n  ✅ Packets sent:    {human_size(meta['original_size'])}")
    print(f"  ✅ Packets received: {human_size(meta['received_size'])}")
    print(f"  ⏱️  Simulated delay: {meta['latency_ms']} ms")
    if meta["bytes_altered"] > 0:
        print(f"  💥 Bytes altered:   {meta['bytes_altered']}")

    log(f"Transmission complete. Attack={attack}, Bytes altered={meta['bytes_altered']}")
    return received_bytes, meta


def stage_integrity(original_hash: str, received_bytes: bytes) -> bool:
    """
    Stage 3 – Verify data integrity with SHA-256.

    Returns:
        is_intact (bool)
    """
    print("\n" + "═"*60)
    print("  🔍  STAGE 3 – INTEGRITY CHECK")
    print("═"*60)

    progress_bar("Verifying hash  ", steps=15)
    is_intact, received_hash = verify_integrity(original_hash, received_bytes)

    print(f"\n  Original hash : {original_hash[:32]}…")
    print(f"  Received hash : {received_hash[:32]}…")

    if is_intact:
        print("\n  ✅  STATUS: DATA INTACT — Safe to decrypt")
        log("Integrity check PASSED – data is unmodified.", "SUCCESS")
    else:
        print("\n  ❌  STATUS: DATA COMPROMISED — Hashes do not match!")
        log("Integrity check FAILED – data was tampered or corrupted!", "ERROR")

    return is_intact


def stage_decrypt(received_bytes: bytes, key: bytes, iv: bytes, is_intact: bool):
    """
    Stage 4 – Decrypt the received cipher-text.

    Even if integrity failed we attempt decryption so the dashboard can
    show the visual corruption — but we flag the result clearly.

    Returns:
        decrypted_bytes (bytes | None)
    """
    print("\n" + "═"*60)
    print("  🔓  STAGE 4 – DECRYPTION")
    print("═"*60)

    if not is_intact:
        print("\n  ⚠️  Attempting decryption of compromised data…")

    progress_bar("Decrypting      ", steps=20)

    try:
        decrypted_bytes = decrypt_image(received_bytes, key, iv)
        save_image_bytes(decrypted_bytes, DECRYPTED_PATH)
        log(f"Decryption successful → {DECRYPTED_PATH}", "SUCCESS")
        return decrypted_bytes
    except ValueError as exc:
        print(f"\n  ❌  Decryption failed: {exc}")
        log(f"Decryption failed: {exc}", "ERROR")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ══════════════════════════════════════════════════════════════════════════════

def render_dashboard(
    image_path: str,
    image_bytes: bytes,
    encrypted_bytes: bytes,
    decrypted_bytes,       # bytes or None
    is_intact: bool,
    meta: dict,
):
    """
    Render a full matplotlib dashboard showing:
      - Original satellite image
      - Encrypted data heatmap preview
      - Decrypted image (or error state)
      - Integrity status banner
      - Size comparison bar chart
      - Transmission metadata
    """
    print("\n" + "═"*60)
    print("  📊  RENDERING VISUAL DASHBOARD")
    print("═"*60)

    # ── colour palette ─────────────────────────────────────────────────────
    BG        = "#0a0e1a"
    PANEL     = "#111827"
    ACCENT    = "#00d4ff"
    SAFE_CLR  = "#00ff99"
    WARN_CLR  = "#ff4466"
    TEXT      = "#e0e8ff"
    MUTED     = "#556080"

    fig = plt.figure(figsize=(18, 11), facecolor=BG)
    fig.suptitle(
        "🛰️  SECURE SPACE IMAGE TRANSMISSION SYSTEM",
        color=ACCENT, fontsize=17, fontweight="bold",
        fontfamily="monospace", y=0.97,
    )

    gs = gridspec.GridSpec(
        3, 4,
        figure=fig,
        hspace=0.55, wspace=0.35,
        left=0.05, right=0.97, top=0.92, bottom=0.06,
    )

    # ── helper to style axes ───────────────────────────────────────────────
    def style_ax(ax, title):
        ax.set_facecolor(PANEL)
        ax.set_title(title, color=ACCENT, fontsize=9,
                     fontfamily="monospace", pad=6)
        for spine in ax.spines.values():
            spine.set_edgecolor(MUTED)

    # ── 1. Original image ──────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0:2, 0:2])
    style_ax(ax1, "[ ORIGINAL SATELLITE IMAGE ]")
    orig_img = bytes_to_pil(image_bytes)
    ax1.imshow(orig_img)
    ax1.axis("off")
    ax1.text(
        0.02, 0.02,
        f"Size: {human_size(len(image_bytes))}  |  {orig_img.size[0]}×{orig_img.size[1]} px",
        transform=ax1.transAxes, color=MUTED, fontsize=7,
        fontfamily="monospace", va="bottom",
    )

    # ── 2. Encrypted data preview ──────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 2])
    style_ax(ax2, "[ ENCRYPTED DATA PREVIEW ]")
    enc_arr = encrypted_preview_array(encrypted_bytes, 128, 192)
    ax2.imshow(enc_arr, cmap="plasma", aspect="auto", interpolation="nearest")
    ax2.axis("off")
    ax2.text(
        0.02, 0.02,
        f"AES-256-CBC  |  {human_size(len(encrypted_bytes))}",
        transform=ax2.transAxes, color=MUTED, fontsize=7,
        fontfamily="monospace", va="bottom",
    )

    # ── 3. Decrypted image ─────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 2])
    style_ax(ax3, "[ DECRYPTED IMAGE ]")
    if decrypted_bytes is not None:
        try:
            dec_img = bytes_to_pil(decrypted_bytes)
            ax3.imshow(dec_img)
            ax3.axis("off")
        except Exception:
            ax3.text(0.5, 0.5, "⚠️\nCORRUPTED",
                     ha="center", va="center", color=WARN_CLR,
                     fontsize=12, fontfamily="monospace",
                     transform=ax3.transAxes)
            ax3.axis("off")
    else:
        ax3.text(0.5, 0.5, "❌\nDECRYPTION\nFAILED",
                 ha="center", va="center", color=WARN_CLR,
                 fontsize=11, fontfamily="monospace",
                 transform=ax3.transAxes)
        ax3.axis("off")

    # ── 4. Integrity status banner ─────────────────────────────────────────
    ax4 = fig.add_subplot(gs[0, 3])
    ax4.set_facecolor(PANEL)
    ax4.axis("off")
    status_color = SAFE_CLR if is_intact else WARN_CLR
    status_icon  = "✅" if is_intact else "❌"
    status_text  = "DATA\nINTACT" if is_intact else "DATA\nCOMPROMISED"
    ax4.text(
        0.5, 0.62, status_icon,
        ha="center", va="center", fontsize=32,
        transform=ax4.transAxes,
    )
    ax4.text(
        0.5, 0.30, status_text,
        ha="center", va="center", fontsize=14, fontweight="bold",
        color=status_color, fontfamily="monospace",
        transform=ax4.transAxes,
    )
    ax4.set_title("[ INTEGRITY STATUS ]", color=ACCENT,
                  fontsize=9, fontfamily="monospace", pad=6)
    for spine in ax4.spines.values():
        spine.set_edgecolor(MUTED)

    # ── 5. Transmission metadata ───────────────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 3])
    ax5.set_facecolor(PANEL)
    ax5.axis("off")
    ax5.set_title("[ TRANSMISSION META ]", color=ACCENT,
                  fontsize=9, fontfamily="monospace", pad=6)
    info_lines = [
        f"  Attack  : {meta['attack_applied'].upper()}",
        f"  Latency : {meta['latency_ms']} ms",
        f"  Sent    : {human_size(meta['original_size'])}",
        f"  Recv    : {human_size(meta['received_size'])}",
        f"  Altered : {meta['bytes_altered']} bytes",
    ]
    for i, line in enumerate(info_lines):
        col = WARN_CLR if ("TAMPER" in line or "NOISE" in line or
                           (meta["bytes_altered"] > 0 and "Altered" in line)) else TEXT
        ax5.text(
            0.05, 0.82 - i * 0.16, line,
            transform=ax5.transAxes, color=col,
            fontsize=8.5, fontfamily="monospace",
        )
    for spine in ax5.spines.values():
        spine.set_edgecolor(MUTED)

    # ── 6. Size comparison bar chart ───────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, :2])
    style_ax(ax6, "[ SIZE COMPARISON — ORIGINAL vs ENCRYPTED ]")
    labels = ["Original Image", "Encrypted (.bin)"]
    values = [len(image_bytes) / 1024, len(encrypted_bytes) / 1024]
    bars   = ax6.bar(labels, values, color=[ACCENT, "#ff9f43"], width=0.4,
                     edgecolor=MUTED, linewidth=0.8)
    ax6.set_ylabel("Size (KB)", color=TEXT, fontsize=8, fontfamily="monospace")
    ax6.tick_params(colors=TEXT, labelsize=8)
    for bar, val in zip(bars, values):
        ax6.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.02,
            f"{val:.1f} KB",
            ha="center", color=TEXT, fontsize=8, fontfamily="monospace",
        )
    ax6.set_facecolor(PANEL)
    ax6.tick_params(axis="x", colors=TEXT)
    for spine in ax6.spines.values():
        spine.set_edgecolor(MUTED)
    ax6.set_ylim(0, max(values) * 1.18)

    # ── 7. Byte-frequency histogram of encrypted data ─────────────────────
    ax7 = fig.add_subplot(gs[2, 2:])
    style_ax(ax7, "[ ENCRYPTED BYTE DISTRIBUTION — UNIFORM = GOOD ]")
    byte_vals = np.frombuffer(encrypted_bytes[:8192], dtype=np.uint8)
    ax7.hist(byte_vals, bins=64, color=ACCENT, alpha=0.85, edgecolor="none")
    ax7.set_xlabel("Byte value (0–255)", color=TEXT, fontsize=8, fontfamily="monospace")
    ax7.set_ylabel("Frequency", color=TEXT, fontsize=8, fontfamily="monospace")
    ax7.tick_params(colors=TEXT, labelsize=7)
    for spine in ax7.spines.values():
        spine.set_edgecolor(MUTED)
    ax7.set_facecolor(PANEL)

    plt.savefig("dashboard.png", dpi=140, bbox_inches="tight", facecolor=BG)
    plt.show()
    log("Dashboard rendered and saved to dashboard.png", "SUCCESS")
    print("\n  📊 Dashboard saved → dashboard.png")


# ══════════════════════════════════════════════════════════════════════════════
# Main entry point
# ══════════════════════════════════════════════════════════════════════════════

def run_pipeline(image_path: str = None, attack: str = "none"):
    """
    Execute the full end-to-end pipeline.

    Args:
        image_path: Path to source image (will prompt if None)
        attack:     "none" | "tamper" | "noise"
    """
    clear_log()

    print("\n" + "╔" + "═"*58 + "╗")
    print("║   🛰️   SECURE SPACE IMAGE TRANSMISSION SYSTEM          ║")
    print("║         Satellite → Encrypted Channel → Ground Station  ║")
    print("╚" + "═"*58 + "╝\n")

    # ── Get image ─────────────────────────────────────────────────────────
    if image_path is None:
        try:
            image_path = upload_image_colab()
        except Exception as exc:
            print(f"  ❌ Could not load image: {exc}")
            sys.exit(1)

    # ── Run stages ────────────────────────────────────────────────────────
    image_bytes, encrypted_bytes, key, iv, original_hash = stage_encrypt(image_path)
    received_bytes, meta                                  = stage_transmit(encrypted_bytes, attack)
    is_intact                                             = stage_integrity(original_hash, received_bytes)
    decrypted_bytes                                       = stage_decrypt(received_bytes, key, iv, is_intact)

    # ── Dashboard ─────────────────────────────────────────────────────────
    render_dashboard(
        image_path, image_bytes, encrypted_bytes,
        decrypted_bytes, is_intact, meta,
    )

    print("\n" + "╔" + "═"*58 + "╗")
    print("║   ✅  PIPELINE COMPLETE                                  ║")
    print(f"║   Log saved → transmission_log.txt                      ║")
    print("╚" + "═"*58 + "╝\n")


# ── CLI usage ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Secure Space Image Transmission System")
    parser.add_argument("--image",  type=str, default=None,
                        help="Path to input image (JPG/PNG). Colab upload dialog if omitted.")
    parser.add_argument("--attack", type=str, default="none",
                        choices=["none", "tamper", "noise"],
                        help="Simulate an attack on the channel (default: none)")
    args = parser.parse_args()

    run_pipeline(image_path=args.image, attack=args.attack)
