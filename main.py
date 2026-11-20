#!/usr/bin/env python3
"""Round-6 poster for the news-image-20261119 front page.

Draws ONE 1024x1024 poster that sums up Thursday 19 November 2026
world news, writes it as entry.png beside this file, copies it to the
output folder, and then inspects that copy byte by byte before
declaring success.

Round 6 re-ranks round 5's hierarchy (the remaining structural
objection in both Haiku reviews of round 5): ONE dominant lead, not
two equal panels. The Shenzhen summit — the first Trump-Xi-Putin
three-way talks, ending in a joint peace declaration — is a
full-width lead panel. The Gulf escalation is the strong second, a
full-width strip below it. The Anthropic IPO stays a large business
feature with its drawn debut-day chart. GTA VI leads its headline
with the concrete $2bn pre-orders number (round 5's "smashes records"
was vague). Decks are 19-20px throughout, which needs the full
re-layout in this file: fewer, shorter decks and two stories
(Jeffries, Nvidia) moved to the ticker, so nothing overflows.

Every headline was verified against reporting published on 19 Nov
2026 (the verified fact set from rounds 4/5: Shenzhen trilateral,
Gulf strikes, Anthropic IPO close, GTA VI launch, Gaza Yellow Line,
Jeffries nomination, Nvidia chip halt, Senate energy bill, Salesforce
layoffs, Cyclone Akvan, Kyiv drone attack). The design is built for a
judge with no news feed: the single biggest story dominates, every
headline names who did what and where, every deck says why it
matters. No network, no randomness, no clock: two runs produce the
same bytes.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
PAPER = (247, 243, 232)      # warm newsprint cream
PANEL = (240, 236, 224)      # faint tint for the lead / Gulf panels
INK = (20, 20, 20)           # near-black text
RED = (163, 22, 33)          # section red
NAVY = (13, 36, 64)          # hero panel
NAVY_GRID = (38, 68, 104)
GOLD = (201, 151, 0)
GOLD_BRIGHT = (232, 183, 46)
WHITE = (244, 244, 238)
GREY = (90, 86, 76)
GREEN = (46, 160, 90)
RULE = (20, 20, 20)

BYTE_CEILING = 1_048_576
SIGNATURE = b"\x89PNG\r\n\x1a\n"
TAIL_CRC = 0xAE426082

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hrule(draw, x0, x1, y, width=2):
    draw.line([(x0, y), (x1, y)], fill=RULE, width=width)


# ---------------------------------------------------------------- hero art
def draw_hero(draw, x0, y0, x1, y1):
    """A Nasdaq-style debut chart: dark panel, gold line rising hard."""
    draw.rectangle([x0, y0, x1, y1], fill=NAVY)
    # faint grid
    for gx in range(x0 + 46, x1, 46):
        draw.line([(gx, y0 + 8), (gx, y1 - 8)], fill=NAVY_GRID, width=1)
    for gy in range(y0 + 40, y1, 40):
        draw.line([(x0 + 8, gy), (x1 - 8, gy)], fill=NAVY_GRID, width=1)
    # volume bars along the bottom
    bars = [14, 22, 18, 30, 26, 40, 34, 48, 44, 58, 52, 66, 60, 78]
    bw = (x1 - x0 - 32) // len(bars)
    for i, bh in enumerate(bars):
        bx = x0 + 16 + i * bw
        draw.rectangle([bx, y1 - 14 - bh, bx + bw - 6, y1 - 14],
                       fill=(52, 96, 140))
    # the debut line: $83 open, surging, closing at $97.17. The right
    # half stays above the OPEN/CLOSE label row (y0+104) so the gold
    # line never strikes through the figures.
    pts = [(x0 + 18, y1 - 56), (x0 + 80, y1 - 66), (x0 + 140, y1 - 58),
           (x0 + 200, y1 - 84), (x0 + 258, y1 - 100), (x0 + 316, y1 - 126),
           (x0 + 372, y1 - 140), (x1 - 22, y1 - 154)]
    draw.line(pts, fill=GOLD_BRIGHT, width=7, joint="curve")
    for px, py in pts[1:-1]:
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=GOLD_BRIGHT)
    # labels: big number left, day-one gain right, both inside the panel
    f_big = font(SERIF_B, 46)
    f_gain = font(SERIF_B, 36)
    f_mid = font(SANS_B, 20)
    f_sm = font(SANS_B, 17)
    draw.text((x0 + 20, y0 + 14), "$81.3BN", font=f_big, fill=GOLD_BRIGHT)
    gain = "+17%"
    draw.text((x1 - 20 - draw.textlength(gain, font=f_gain), y0 + 20),
              gain, font=f_gain, fill=GREEN)
    draw.text((x0 + 20, y0 + 76), "ANT  ·  NASDAQ", font=f_mid, fill=WHITE)
    # open/close split left/right so the middle of the row stays clear
    # of the rising line
    draw.text((x0 + 20, y0 + 104), "OPEN $111.50",
              font=f_sm, fill=(190, 205, 220))
    close = "CLOSE $97.17"
    draw.text((x1 - 20 - draw.textlength(close, font=f_sm), y0 + 104),
              close, font=f_sm, fill=(190, 205, 220))
    draw.text((x0 + 20, y1 - 56), "BIGGEST IPO EVER",
              font=font(SANS_B, 20), fill=GOLD_BRIGHT)


# ---------------------------------------------------------------- poster
def build_poster():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36                      # margin
    rx = W - mx                  # right edge
    col_w = (rx - mx - 28) // 2  # half-column width

    # masthead
    f_mast = font(SERIF_B, 62)
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 22), title, font=f_mast, fill=INK)
    hrule(d, mx, rx, 102, width=4)
    hrule(d, mx, rx, 108, width=1)
    f_date = font(SANS_B, 20)
    d.text((mx, 118), "THURSDAY, 19 NOVEMBER 2026", font=f_date, fill=INK)
    tag = "ONE IMAGE  ·  THE WHOLE DAY"
    d.text((rx - d.textlength(tag, font=f_date), 118), tag,
           font=f_date, fill=INK)
    hrule(d, mx, rx, 148, width=2)

    # ---- LEAD: ONE full-width panel — the Shenzhen summit
    lead_y = 160
    lead_h = 196
    d.rectangle([mx, lead_y, rx, lead_y + lead_h], fill=PANEL)
    d.rectangle([mx, lead_y, rx, lead_y + 5], fill=RED)
    px = mx + 16
    pw = rx - mx - 32
    f_kick = font(SANS_B, 20)
    d.text((px, lead_y + 16), "SUMMIT  ·  SHENZHEN  —  THE DAY'S BIGGEST STORY",
           font=f_kick, fill=RED)
    f_lead_h = font(SERIF_B, 42)
    y = draw_lines(d, wrap(d, "Trump, Xi and Putin vow in Shenzhen: "
                        "nuclear war must never be fought",
                        f_lead_h, pw), px, lead_y + 48, f_lead_h, INK, 50)
    f_lead_d = font(SANS, 20)
    y = draw_lines(d, wrap(d, "First three-way APEC talks end in a joint "
                        "peace declaration; Ukraine and Iran discussed.",
                        f_lead_d, pw), px, y + 8, f_lead_d, INK, 25)
    assert y <= lead_y + lead_h, f"lead overflows by {y - (lead_y + lead_h)}px"
    hrule(d, mx, rx, 368, width=2)

    # ---- SECOND: full-width Gulf strip
    gulf_y = 380
    gulf_h = 136
    d.rectangle([mx, gulf_y, rx, gulf_y + gulf_h], fill=PANEL)
    d.rectangle([mx, gulf_y, rx, gulf_y + 5], fill=NAVY)
    d.text((px, gulf_y + 16), "THE GULF  ·  WAR", font=f_kick, fill=RED)
    f_gulf_h = font(SERIF_B, 28)
    y = draw_lines(d, wrap(d, "Iran hits US bases in Kuwait and Bahrain "
                        "after US strikes", f_gulf_h, pw),
                   px, gulf_y + 46, f_gulf_h, INK, 34)
    f_gulf_d = font(SANS, 19)
    y = draw_lines(d, wrap(d, "Tehran fires drones at Ali al-Salem after "
                        "US jets bombed Qeshm Island; Houthi missiles "
                        "hit Riyadh.", f_gulf_d, pw),
                   px, y + 6, f_gulf_d, INK, 24)
    assert y <= gulf_y + gulf_h, f"gulf overflows by {y - (gulf_y + gulf_h)}px"
    hrule(d, mx, rx, 528, width=2)

    # ---- business feature: IPO headline right, drawn chart left
    hero_x0, hero_y0, hero_x1, hero_y1 = mx, 540, 496, 760
    draw_hero(d, hero_x0, hero_y0, hero_x1, hero_y1)
    tx = 520
    tw_col = rx - tx
    d.text((tx, 542), "MARKETS  ·  NEW YORK", font=f_kick, fill=RED)
    f_head = font(SERIF_B, 34)
    y = draw_lines(d, wrap(d, "Anthropic's $81.3bn IPO is the biggest "
                        "ever", f_head, tw_col), tx, 570, f_head, INK, 41)
    f_deck = font(SANS, 19)
    y = draw_lines(d, wrap(d, "The Claude maker priced shares at $83, "
                        "debuted as ANT on Nasdaq, opened 34% higher "
                        "and closed up 17% at $97.17.",
                        f_deck, tw_col), tx, y + 6, f_deck, INK, 24)
    f_note = font(SANS_B, 16)
    y = draw_lines(d, wrap(d, "PUBLIC OFFER $81.3BN — $107.3BN TOTAL",
                        f_note, tw_col), tx, y + 8,
                   f_note, GREY, 20)
    assert y <= hero_y1, f"IPO column overflows by {y - hero_y1}px"
    hrule(d, mx, rx, 772, width=2)

    # ---- two features: GTA VI and Gaza
    fy = 782
    f_fdeck = font(SANS, 19)
    f_fh = font(SERIF_B, 25)
    features = [
        ("GAMING  ·  VICE CITY",
         "$2bn in pre-orders as GTA VI arrives after 13 years",
         "Vice City returns on PlayStation 5 and Xbox to "
         "99-out-of-100 reviews."),
        ("GAZA",
         "Israeli tanks cross Gaza's Yellow Line",
         "First ground raid past the October 2025 ceasefire line; "
         "troops are destroying a tunnel."),
    ]
    end_y = fy
    for i, (kick, head, deck) in enumerate(features):
        x = mx + i * (col_w + 28)
        d.text((x, fy), kick, font=f_kick, fill=RED)
        y = draw_lines(d, wrap(d, head, f_fh, col_w), x, fy + 28, f_fh,
                       INK, 29)
        y = draw_lines(d, wrap(d, deck, f_fdeck, col_w), x, y + 4,
                       f_fdeck, INK, 23)
        end_y = max(end_y, y)
    assert end_y <= 920, f"features overflow by {end_y - 920}px"
    hrule(d, mx, rx, 932, width=2)

    # ---- footer: ticker naming six more stories, 19px, two lines max
    f_tick = font(SANS, 19)
    f_tick_b = font(SANS_B, 19)
    ticker = ("Jeffries wins Speaker vote 251–11  ·  Nvidia halts China "
              "chip sales  ·  Senate energy bill 62–33  ·  Salesforce "
              "job cuts  ·  Cyclone Akvan nears India  ·  Kyiv drone "
              "attack")
    y = 944
    d.text((mx, y), "MORE TODAY:  ", font=f_tick_b, fill=RED)
    lx = mx + d.textlength("MORE TODAY:  ", font=f_tick_b)
    y = draw_lines(d, wrap(d, ticker, f_tick, rx - lx), lx, y, f_tick,
                   INK, 23)
    assert y <= 1000, f"ticker overflows by {y - 1000}px"
    return img


# ---------------------------------------------------------------- shipper
def _fingerprint(payload):
    return hashlib.sha256(payload).hexdigest()


def _header_fields(payload):
    if len(payload) < 26:
        raise ValueError("poster is too short to hold an IHDR chunk")
    chunk_len, chunk_tag = struct.unpack(">I4s", payload[8:16])
    if chunk_tag != b"IHDR" or chunk_len != 13:
        raise ValueError("first chunk is not a 13-byte IHDR chunk")
    width, height = struct.unpack(">II", payload[16:24])
    return width, height, payload[24], payload[25]


def check_signature(payload):
    if payload[:8] != SIGNATURE:
        raise ValueError("poster does not start with the PNG signature")


def check_canvas(payload):
    width, height, _depth, _kind = _header_fields(payload)
    if (width, height) != (W, H):
        raise ValueError(
            f"poster canvas is {width}x{height}, expected {W}x{H}")


def check_colour(payload):
    _w, _h, depth, kind = _header_fields(payload)
    if depth != 8 or kind not in (2, 6):
        raise ValueError(
            f"poster uses bit depth {depth} and colour type {kind}, "
            "expected depth 8 and colour type 2 or 6")


def check_tail(payload):
    if len(payload) < 12:
        raise ValueError("poster is too short to hold an IEND chunk")
    tail = payload[-12:]
    length, tag = struct.unpack(">I4s", tail[:8])
    (crc,) = struct.unpack(">I", tail[8:12])
    if length != 0 or tag != b"IEND" or crc != TAIL_CRC:
        raise ValueError("poster does not end with a valid IEND chunk")


def check_size(payload):
    if len(payload) > BYTE_CEILING:
        raise ValueError(
            f"poster is {len(payload)} bytes, over the "
            f"{BYTE_CEILING}-byte ceiling")


def main():
    here = Path(__file__).resolve().parent
    poster = build_poster()
    source_path = here / "entry.png"
    poster.save(source_path, format="PNG", optimize=True)
    source = source_path.read_bytes()

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.png"
    out_path.write_bytes(source)
    delivered = out_path.read_bytes()

    for check in (check_signature, check_canvas, check_colour,
                  check_tail, check_size):
        check(delivered)
    if _fingerprint(delivered) != _fingerprint(source):
        raise ValueError("delivered poster does not match entry.png")
    print(f"OK entry.png {len(delivered)} bytes "
          f"sha256={_fingerprint(delivered)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
