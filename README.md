# Sunday 22 November 2026: 38 stories, 8 regions

A one-day world news front page for the make.fun competition
"news-image-20261122" — sum up 22 November's world news in one image.

The image shows: a giant date masthead, the three lead stories
(COP31 collapses with no deal, 186 drones over Ukraine, the Russian
warship Merkury sunk at Benghazi) as drawn panels, a numbers strip,
a region bar, the full list of 38 verified stories across 8 regions,
a dot-matrix world map with pins, an ALSO ON list, a red DATE CHECK
box listing big stories that are NOT 22 November and were left out
on purpose, and a footer stating every story happened, or was first
reported, on Sunday 22 November 2026.

## Run

```sh
python3 main.py
```

Writes `entry.png` (1024x1024, under 1 MiB) to `$MAKEFUN_OUTPUT_DIR`,
or `/output` when that variable is not set (run locally with
`MAKEFUN_OUTPUT_DIR=out python3 main.py`). Python 3.13 standard
library only, no network: the program draws everything with its own
PNG encoder, rasteriser and 5x7 bitmap font. Two runs write
byte-identical files.
