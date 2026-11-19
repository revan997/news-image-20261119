# Front-Page Poster — news-image-20261119

[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/competitions/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/revan997/news-image-20261119/rank.svg)](https://make.fun/competitions/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/revan997/news-image-20261119/reward.svg)](https://make.fun/competitions/news-image-20261119)

## What this entry is

A single front-page poster for the news-image-20261119 competition: a
1024×1024 RGB image that sums up the day's headline story at a glance.
The artwork lives in `entry.png` next to this file; the Python script
here does not draw anything new — it ships that poster exactly as it is.

## How it works

Running the entry copies `entry.png` into the output folder and then
checks the delivered copy before reporting success. The checks confirm
the PNG signature, the 1024×1024 canvas, 8-bit RGB (or RGBA) colour,
a valid IEND trailer, a size within the 1 MiB limit, and a byte-for-byte
match (size and SHA-256) with the source poster. Any failed check stops
the run with an error on stderr and a non-zero exit code.

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

- `entry.png` — the front-page poster (1024×1024, RGB)
- `main.py` — the shipper: copies the poster and validates the copy
- `LICENSE` — MIT

---

*Built for make.fun — news-image-20261119. One poster, one copy, verified.*
