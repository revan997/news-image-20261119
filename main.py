#!/usr/bin/env python3
"""news-image-20261119 entry: copy the front-page image to /output/entry.png.

The image is a newspaper front page summing up Thursday 19 November 2026:
lead story Anthropic's record $81.3bn IPO, priced at $83 a share and
debuting on Nasdaq today as ANT; plus the first-ever Trump-Xi-Putin
three-way talks at the APEC summit in Shenzhen, the GTA VI global
rollout, Israeli tanks crossing the Yellow Line into central Gaza,
Jeffries' nomination for Speaker, Iran widening its attacks on Gulf
states, and Cyclone Akvan nearing the Indian coast. Deterministic,
no network.

Usage: python3 main.py
  Copies entry.png (next to this file) to $MAKEFUN_OUTPUT_DIR/entry.png
  (default /output/entry.png), then verifies the copy: it must start with
  the PNG magic bytes, be exactly 1024x1024 pixels, its IHDR color type
  must be 2 (RGB) or 6 (RGBA) with bit depth 8, be at most 1 MiB
  (1048576 bytes), it must end with a valid
  IEND chunk (12-byte trailer: length 0, type IEND, CRC 0xAE426082), and
  its size and SHA-256 must match the source. Exits non-zero with a
  message on stderr if verification fails.
"""
import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1048576  # competition gate: image must be at most 1 MiB

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

SRC = HERE / "entry.png"
DST = OUT / "entry.png"


IEND_TRAILER = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", 0xAE426082)
ALLOWED_COLOR_TYPES = (2, 6)  # RGB, RGBA
EXPECTED_BIT_DEPTH = 8


def png_dimensions(data):
    """Read width and height from the PNG IHDR chunk."""
    if len(data) < 33 or data[:8] != PNG_MAGIC or data[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def png_ihdr_color(data):
    """Read (bit depth, color type) from the PNG IHDR chunk.

    IHDR layout: width (4), height (4), bit depth (1), color type (1),
    so bit depth is byte 24 and color type is byte 25 of the file.
    """
    if len(data) < 33 or data[:8] != PNG_MAGIC or data[12:16] != b"IHDR":
        return None
    return data[24], data[25]


OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SRC, DST)

# Verify the copy: PNG magic bytes, 1024x1024 dimensions, IHDR color
# type 2 (RGB) or 6 (RGBA) with bit depth 8, a valid IEND trailer,
# size, and SHA-256 must all match the source.
src_bytes = SRC.read_bytes()
dst_bytes = DST.read_bytes()
if not dst_bytes.startswith(PNG_MAGIC):
    print("error: output is not a PNG (bad magic bytes)", file=sys.stderr)
    sys.exit(1)
dims = png_dimensions(dst_bytes)
if dims != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
    print(f"error: output dimensions {dims} != "
          f"({EXPECTED_WIDTH}, {EXPECTED_HEIGHT})", file=sys.stderr)
    sys.exit(1)
color = png_ihdr_color(dst_bytes)
if color is None or color[1] not in ALLOWED_COLOR_TYPES \
        or color[0] != EXPECTED_BIT_DEPTH:
    print(f"error: unexpected IHDR color (bit depth, color type) "
          f"{color}, want (8, 2 or 6)", file=sys.stderr)
    sys.exit(1)
if len(dst_bytes) > MAX_BYTES:
    print(f"error: output size {len(dst_bytes)} exceeds the 1 MiB cap "
          f"({MAX_BYTES} bytes)", file=sys.stderr)
    sys.exit(1)
if not dst_bytes.endswith(IEND_TRAILER):
    print("error: output does not end with a valid IEND chunk",
          file=sys.stderr)
    sys.exit(1)
if len(dst_bytes) != len(src_bytes):
    print(f"error: output size {len(dst_bytes)} != source size "
          f"{len(src_bytes)}", file=sys.stderr)
    sys.exit(1)
if hashlib.sha256(dst_bytes).hexdigest() != \
        hashlib.sha256(src_bytes).hexdigest():
    print("error: output SHA-256 does not match the source",
          file=sys.stderr)
    sys.exit(1)
print(f"wrote {DST} ({len(dst_bytes)} bytes, "
      f"sha256 {hashlib.sha256(dst_bytes).hexdigest()})")
