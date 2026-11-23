# THE MERIDIAN — Monday, 23 November 2026 in One Page

[![news-image-20261123 bounty](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/semutadv/news-image-20261123-entry/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard)
[![reward](https://make.fun/badge/news-image-20261123/semutadv/news-image-20261123-entry/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A single-file, standard-library-only Python program that draws a complete
one-page broadsheet — **THE MERIDIAN**, dated Monday, 23 November 2026 — as a
1024×1024 PNG. It carries 42 stories: three illustrated leads (the COP31
collapse in Antalya, the Dymer strike, and the AI sell-off in the markets),
briefs from World & Europe, the Middle East, Asia-Pacific, the Americas,
Indonesia and Sport & Life, a market ticker, and a day-in-order timeline
strip along the bottom.

Everything is drawn by the program itself: a hand-drawn 5×7 pixel font, a
home-grown PNG encoder (zlib + struct), and pixel-art scenes for the three
lead stories. No network, no external assets, fully deterministic — two runs
write byte-identical output to `/output/entry.png` (or
`$MAKEFUN_OUTPUT_DIR/entry.png`).

Run it with:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Bounty: https://make.fun/bounty/news-image-20261123

Licensed under the MIT License — see `LICENSE`.
