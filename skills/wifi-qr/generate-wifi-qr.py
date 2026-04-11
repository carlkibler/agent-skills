#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "qrcode[pil]",
#   "Pillow",
# ]
# ///

import argparse
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def wifi_payload(ssid: str, password: str, security: str) -> str:
    def escape(s: str) -> str:
        return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace('"', '\\"')

    sec = security.upper()
    if sec not in ("WPA", "WEP", "NOPASS", ""):
        print(f"Warning: unknown security type '{security}', defaulting to WPA", file=sys.stderr)
        sec = "WPA"

    if sec == "NOPASS":
        return f"WIFI:T:nopass;S:{escape(ssid)};;"
    return f"WIFI:T:{sec};S:{escape(ssid)};P:{escape(password)};;"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a WiFi QR code PNG")
    parser.add_argument("--ssid", required=True, help="Network name (SSID)")
    parser.add_argument("--password", default="", help="Network password")
    parser.add_argument("--security", default="WPA", help="Security type: WPA, WEP, or nopass (default: WPA)")
    parser.add_argument("--output", required=True, help="Output PNG file path")
    parser.add_argument("--size", type=int, default=6, help="Module size in pixels (default: 6)")
    parser.add_argument("--border", type=int, default=2, help="Border in modules (default: 2)")
    args = parser.parse_args()

    payload = wifi_payload(args.ssid, args.password, args.security)

    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_M,
        box_size=args.size,
        border=args.border,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print(f"Saved {out} ({out.stat().st_size} bytes)  [{payload}]")


if __name__ == "__main__":
    main()
