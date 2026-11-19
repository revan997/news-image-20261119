#!/usr/bin/env python3
"""Poster shipper for the news-image-20261119 front page.

Reads the poster that sits beside this file, places an exact copy in
the output folder, and then inspects that copy byte by byte before
declaring success. Nothing is generated here; the artwork already
exists and this script only moves it and proves the move was clean.
"""

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

POSTER_NAME = "entry.png"
POSTER_EDGE = 1024
POSTER_DEPTH = 8
ALLOWED_KINDS = (2, 6)
BYTE_CEILING = 1_048_576
SIGNATURE = b"\x89PNG\r\n\x1a\n"
TAIL_CRC = 0xAE426082


def _fingerprint(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _header_fields(payload: bytes):
    """Pull width, height, bit depth and colour kind out of the IHDR."""
    if len(payload) < 26:
        raise ValueError("poster is too short to hold an IHDR chunk")
    chunk_len, chunk_tag = struct.unpack(">I4s", payload[8:16])
    if chunk_tag != b"IHDR" or chunk_len != 13:
        raise ValueError("first chunk is not a 13-byte IHDR chunk")
    width, height = struct.unpack(">II", payload[16:24])
    return width, height, payload[24], payload[25]


def check_signature(payload: bytes) -> None:
    if payload[:8] != SIGNATURE:
        raise ValueError("poster does not start with the PNG signature")


def check_canvas(payload: bytes) -> None:
    width, height, _depth, _kind = _header_fields(payload)
    if (width, height) != (POSTER_EDGE, POSTER_EDGE):
        raise ValueError(
            f"poster canvas is {width}x{height}, expected "
            f"{POSTER_EDGE}x{POSTER_EDGE}"
        )


def check_colour(payload: bytes) -> None:
    _w, _h, depth, kind = _header_fields(payload)
    if depth != POSTER_DEPTH or kind not in ALLOWED_KINDS:
        raise ValueError(
            f"poster uses bit depth {depth} and colour type {kind}, "
            f"expected depth {POSTER_DEPTH} and colour type 2 or 6"
        )


def check_tail(payload: bytes) -> None:
    if len(payload) < 12:
        raise ValueError("poster is too short to hold an IEND chunk")
    tail = payload[-12:]
    length, tag = struct.unpack(">I4s", tail[:8])
    crc, = struct.unpack(">I", tail[8:12])
    if length != 0 or tag != b"IEND" or crc != TAIL_CRC:
        raise ValueError("poster does not end with a valid IEND chunk")


def check_weight(payload: bytes) -> None:
    if len(payload) > BYTE_CEILING:
        raise ValueError(
            f"poster is {len(payload)} bytes, over the "
            f"{BYTE_CEILING} byte limit"
        )


def check_matches_source(payload: bytes, origin: bytes) -> None:
    if len(payload) != len(origin):
        raise ValueError(
            f"copy is {len(payload)} bytes but the source is "
            f"{len(origin)} bytes"
        )
    if _fingerprint(payload) != _fingerprint(origin):
        raise ValueError("copy sha256 does not match the source poster")


def inspect_copy(payload: bytes, origin: bytes) -> None:
    """Run every named check in order; the first failure aborts."""
    checks = [
        ("signature", lambda blob: check_signature(blob)),
        ("canvas", lambda blob: check_canvas(blob)),
        ("colour", lambda blob: check_colour(blob)),
        ("tail", lambda blob: check_tail(blob)),
        ("weight", lambda blob: check_weight(blob)),
    ]
    for label, fn in checks:
        try:
            fn(payload)
        except ValueError as exc:
            raise ValueError(f"{label} check failed: {exc}") from exc
    check_matches_source(payload, origin)


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / POSTER_NAME
    if not source.is_file():
        print(f"error: source poster missing: {source}", file=sys.stderr)
        return 1
    try:
        origin = source.read_bytes()
    except OSError as exc:
        print(f"error: cannot read source poster: {exc}", file=sys.stderr)
        return 1

    out_folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    target = out_folder / POSTER_NAME
    try:
        out_folder.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        delivered = target.read_bytes()
    except OSError as exc:
        print(f"error: cannot deliver poster to {target}: {exc}", file=sys.stderr)
        return 1

    try:
        inspect_copy(delivered, origin)
    except ValueError as exc:
        print(f"error: delivered poster failed validation: {exc}", file=sys.stderr)
        return 1

    print(
        f"ok: {target} ({len(delivered)} bytes, "
        f"sha256={_fingerprint(delivered)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
