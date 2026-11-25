# The World Today — 25 November 2026

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)

Sum up 25 November's world news in one image.

A Python program that draws a newspaper front page — masthead, one lead
story, five more stories and an "Also Today" strip — as a single
1024x1024 PNG. The news it sums up: a Houthi drone strike on Riyadh's
PIF Tower, tankers hitting mines in the Strait of Hormuz, Zelenskiy's
confirmation of a ship strike in the Gulf of Finland, Huawei's conviction
in a US criminal trial, the first Pakistani in orbit aboard Shenzhou-24,
and an AI sell-off on Wall Street. Pure PIL, no network at runtime, fully
deterministic: two runs write byte-identical output.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024 PNG, under 1 MiB).

## Entry

Built for the [make.fun](https://make.fun) bounty
[news-image-20261125](https://make.fun/bounty/news-image-20261125).
