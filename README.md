# 🛰️ Secure Space Image Transmission System

> **AES-256 encryption · SHA-256 integrity · Attack simulation · Visual dashboard**
>
> A cybersecurity + space science project that simulates how satellite agencies
> securely transmit telescope/satellite images from space to a ground station.

---

## 📌 Project Overview

When a satellite captures an image of Earth (or deep space), that data must
travel thousands of kilometres over radio links that any adversary could
intercept.  This project simulates that journey end-to-end:

```
[Satellite]  ──encrypt──►  [Insecure Channel]  ──decrypt──►  [Ground Station]
                AES-256                                          SHA-256 check
```

Every stage is visualised in a **matplotlib dashboard** and every event is
saved to a timestamped log file.

---

## ✨ Features

| # | Feature | Detail |
|---|---------|--------|
| 1 | **Image upload** | JPG / PNG via Colab widget or local path |
| 2 | **AES-256-CBC encryption** | Random key + IV per session; saves `.bin` |
| 3 | **Transmission simulation** | Configurable latency; optional attacks |
| 4 | **Attack simulation** | `tamper` (byte flip) · `noise` (bit noise) |
| 5 | **SHA-256 integrity check** | Pre/post hash comparison; SAFE / COMPROMISED banner |
| 6 | **AES decryption** | Reconstructs original image bytes |
| 7 | **Visual dashboard** | 7-panel matplotlib figure (dark space theme) |
| 8 | **Size comparison** | Bar chart: original vs encrypted KB |
| 9 | **Byte-distribution histogram** | Uniform distribution = strong encryption |
| 10 | **Logging** | Timestamped `transmission_log.txt` |

---

## 🗂️ Project Structure

```
secure_space/
│
├── main.py                              # Pipeline orchestrator (CLI entry-point)
├── encryption.py                        # AES-256-CBC encrypt + key generation
├── decryption.py                        # AES-256-CBC decrypt
├── integrity.py                         # SHA-256 hash + verify
├── transmission.py                      # Channel simulation + attack modes
├── utils.py                             # Logging, image I/O, visualisation helpers
│
├── Secure_Space_Image_Transmission.ipynb  # ← Open this in Google Colab!
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Library |
|-------|---------|
| Encryption | `pycryptodome` (AES-256-CBC) |
| Integrity | `hashlib` (SHA-256, stdlib) |
| Image processing | `Pillow` |
| Numerics | `NumPy` |
| Visualisation | `Matplotlib` |
| Runtime | Python 3.9+ |

---

## 🚀 How to Run — Google Colab (recommended)

### Option A — Notebook (easiest)

1. Open [Google Colab](https://colab.research.google.com/)
2. **File → Upload notebook** → select `Secure_Space_Image_Transmission.ipynb`
3. Run **Cell 1** to install dependencies
4. Run **Cell 2** to write source files
5. Run **Cell 3** to upload your image
6. *(Optional)* Edit `ATTACK_MODE` in **Cell 4** — `"none"` / `"tamper"` / `"noise"`
7. Run **Cell 5** — watch the full pipeline execute and the dashboard render
8. Run **Cell 6** to download all outputs

### Option B — Command line

```bash
# Install dependencies
pip install -r requirements.txt

# Run with no attack
python main.py --image my_satellite_image.jpg

# Run with tampering attack
python main.py --image my_satellite_image.jpg --attack tamper

# Run with noise injection
python main.py --image my_satellite_image.jpg --attack noise
```

---

## 📸 Screenshots

> *(Replace the placeholders below with actual screenshots from your run)*

### Dashboard — No Attack (Data Intact)
```
[ Screenshot placeholder — dashboard_safe.png ]
```

### Dashboard — Tamper Attack (Data Compromised)
```
[ Screenshot placeholder — dashboard_tamper.png ]
```

### Log file excerpt
```
[2024-01-15 14:32:01] [INFO]    Image loaded: satellite.jpg (142.3 KB)
[2024-01-15 14:32:01] [INFO]    AES-256 key and IV generated.
[2024-01-15 14:32:01] [SUCCESS] Encryption complete → encrypted_image.bin (142.4 KB)
[2024-01-15 14:32:01] [INFO]    Pre-TX SHA-256: a3f8c2d19b4e7…
[2024-01-15 14:32:02] [WARNING] Attack simulation enabled: tamper
[2024-01-15 14:32:02] [INFO]    Transmission done. Attack=tamper, Altered=142
[2024-01-15 14:32:02] [ERROR]   Integrity FAILED — data tampered!
[2024-01-15 14:32:02] [ERROR]   Decryption failed: data was corrupted or tampered
[2024-01-15 14:32:02] [SUCCESS] Dashboard rendered → dashboard.png
```

---

## 🔐 Security Details

### Encryption — AES-256-CBC
- **Key size**: 256 bits (32 bytes) — generated via `os.urandom()`
- **IV**: 128 bits (16 bytes) — fresh random IV every run
- **Padding**: PKCS#7
- **Mode**: CBC (Cipher Block Chaining) — each block depends on the previous

### Integrity — SHA-256
- Hash computed on the **cipher-text** before transmission
- Re-computed on the **received bytes** at the ground station
- A single altered bit produces a completely different digest — 100% detectable

### Attack Modes
| Mode | Mechanism | Detectable? |
|------|-----------|-------------|
| `tamper` | Randomly flips ~0.1% of bytes | ✅ Always |
| `noise` | XOR bit-flip noise at 0.2% | ✅ Always |
| `none` | Clean channel | ✅ N/A |

---

## 📊 Output Files

| File | Description |
|------|-------------|
| `encrypted_image.bin` | AES-256 cipher-text |
| `decrypted_image.png` | Reconstructed image |
| `dashboard.png` | Visual report (saved at 140 dpi) |
| `transmission_log.txt` | Timestamped event log |

---

## 🔭 Future Improvements

- [ ] **RSA key exchange** — encrypt the AES key with the ground station's public key
- [ ] **TLS-style handshake** simulation before data transfer
- [ ] **HMAC** in addition to SHA-256 for authenticated integrity
- [ ] **Streamlit web UI** — sliders for attack intensity, drag-and-drop upload
- [ ] **Multi-band image support** — simulate hyperspectral satellite imagery
- [ ] **Packet-level simulation** — split image into UDP-style packets, drop/reorder
- [ ] **Real satellite imagery** — integrate NASA Earthdata API for live images
- [ ] **GPU acceleration** — batch-encrypt multiple images in parallel with PyCUDA

---

## 👤 Author

Built as a cybersecurity × space science demonstration project.
Suitable for academic portfolios, GitHub showcases, and learning AES/SHA internals.

---

## 📄 License

MIT — free to use, modify, and distribute with attribution.
