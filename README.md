# demo.siliconwat.dev

Drawings of `ocr.siliconwat.dev`: a free page that reads Pāli and Khmer printed in Khmer script (the Buddhist Institute edition of the Tipiṭaka, 1927–69) in the reader's own browser. Every state on a phone in English and Khmer, the empty and result screens on a computer, and one dark pass. These are drawings. They read nothing and charge nothing, and nothing here is live.

**Front door:** <https://demo.siliconwat.dev/> · **The wall** (every screen at once): <https://demo.siliconwat.dev/wall.html>

## Rebuild

```sh
python3 -m http.server 8333 &      # measure.py reads the boards over HTTP
python3 build-boards.py            # the boards + board.css + canvas.json, from the brand layer
python3 measure.py                 # each board's real height → heights.json
python3 build-boards.py            # again, so canvas.json carries the measured heights
python3 build-index.py && python3 build-wall.py   # the front door and the wall, generated from canvas.json
python3 build-og.py && python3 build-icons.py     # the link-preview card, the icons, the manifest
node scripts/check-brand.mjs       # the vendored brand layer still matches brand.lock
```

⛔ Never hand-edit a generated file (`*.html`, `board.css`, `canvas.json`, `heights.json`, the icons, `og.png`). Edit `build-boards.py`, `board.base.css` or `brand.py` (this surface's own colors and the placeholder icon live there, in one block).

## What the build refuses

*Sign in*, the regulated words, a percentage outside the About screen (a progress figure), a countdown, a streak or a ranking, an AI model or vendor named as an author, and the heart, in the rendered text of every board; and the B-Emblem's path anywhere (it is HeartBank's mark; this is a Silicon Wat surface). In Khmer, the word for a bank.

The icon is a placeholder until Silicon Wat's own mark is settled. The Khmer is our own draft until a native reader approves it, and every Khmer board says so. The sample page is the opening of a sutta in Pāli; the dictionary entry is quoted from the data `khmer.siliconwat.dev` already publishes; file names, page counts and the question asked are made up. Where a drawing and the memory disagree, memory is canonical. The spec these follow is private. This repo is public.
