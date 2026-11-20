# Front-Page Poster — news-image-20261119 (Round 4)

[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/competitions/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/revan997/news-image-20261119/rank.svg)](https://make.fun/competitions/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/revan997/news-image-20261119/reward.svg)](https://make.fun/competitions/news-image-20261119)

## What this entry is

A single front-page poster for the news-image-20261119 competition: a
1024×1024 RGB image that sums up Thursday 19 November 2026 world news
at a glance. It is drawn from scratch by `main.py` — no copied image,
no network, no randomness — so two runs produce the same bytes.

The page is built for a reader with no news feed. The top story
dominates: a debut-day chart for Anthropic's $81.3bn IPO, the biggest
in history, with the price, the ticker and the first-day move printed
on the chart itself. Below it, two large features (the first Trump–Xi–
Putin three-way talks in Shenzhen; GTA VI's launch after 13 years),
four more stories with full context in every deck (Gaza's Yellow Line,
Iran's strikes on a US base in Kuwait, Jeffries' Speaker nomination,
Nvidia halting AI chip sales to China), and a legible ticker of four
more items (Senate energy bill, Salesforce layoffs, Cyclone Akvan,
the Kyiv drone attack). Every headline names who did what and where;
every deck says why it matters. All eleven stories were verified
against reporting published on 19 November 2026.

## How it works

Running the entry draws the poster, writes it as `entry.png` beside
the script, copies it into the output folder, and then checks the
delivered copy before reporting success. The checks confirm the PNG
signature, the 1024×1024 canvas, 8-bit RGB (or RGBA) colour, a valid
IEND trailer, a size within the 1 MiB limit, and a byte-for-byte match
(size and SHA-256) with the source poster. Any failed check stops the
run with an error on stderr and a non-zero exit code.

## Running it

```sh
python3 main.py
```

By default the poster lands at `/output/entry.png`. To send it
somewhere else, set the output folder first:

```sh
MAKEFUN_OUTPUT_DIR=/tmp/my-output python3 main.py
```

A successful run prints a one-line confirmation with the byte size
and the SHA-256 of the delivered poster.

## Files in this repo

- `entry.png` — the front-page poster (1024×1024, RGB), drawn by main.py
- `main.py` — the poster generator and shipper: draws, delivers, validates
- `LICENSE` — MIT

---

*Built for make.fun — news-image-20261119. One poster, drawn fresh, verified.*
