from __future__ import annotations
import base64
import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def b64url_decode(value: str) -> bytes:
    value += "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value.encode("ascii"))

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("output path required")
    payload = os.environ.get("TERMINAL_PAYLOAD", "")
    key_text = os.environ.get("TERMINAL_COMMAND_KEY", "")
    if not payload or not key_text:
        raise SystemExit("terminal encryption configuration missing")
    key = base64.b64decode(key_text)
    if len(key) != 32:
        raise SystemExit("TERMINAL_COMMAND_KEY must decode to 32 bytes")
    raw = b64url_decode(payload)
    if len(raw) < 13:
        raise SystemExit("invalid encrypted payload")
    iv, ciphertext = raw[:12], raw[12:]
    plaintext = AESGCM(key).decrypt(iv, ciphertext, None)
    Path(sys.argv[1]).write_bytes(plaintext)
    return 0
if __name__ == "__main__": raise SystemExit(main())
