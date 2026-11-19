#!/usr/bin/env python3
"""Generate the favicon set and the web app manifest from the PLACEHOLDER icon in brand.py.

    python3 build-icons.py

Writes favicon.svg · favicon-96x96.png · apple-touch-icon.png (180) · icon-192.png · icon-512.png · site.webmanifest.
The PNGs are screenshots of one HTML tile in headless Chrome, so they cannot drift from the SVG.

⚠️ The icon is a placeholder (a page with three printed lines). Silicon Wat's own mark is not settled, and the B-Emblem
is HeartBank's, so it is never used here. When the mark is settled, change ICON_GLYPH in brand.py and rerun this.
"""
import io, json, os, subprocess, sys, tempfile
from brand import ICON_GLYPH, ACCENT, tok

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BG = tok("l-bg")
GLYPH = ICON_GLYPH.format(c=ACCENT)

svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="5" fill="%s"/>%s</svg>'
       % (BG, GLYPH))
io.open(os.path.join(HERE, "favicon.svg"), "w", encoding="utf-8").write(svg + "\n")

if not os.path.exists(CHROME):
    sys.exit("Chrome not found at %s" % CHROME)
for name, px, pad in (("favicon-96x96.png", 96, 0), ("apple-touch-icon.png", 180, .12), ("icon-192.png", 192, .12),
                      ("icon-512.png", 512, .12)):
    tile = ('<!doctype html><html><body style="margin:0;background:%s">'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s" width="%d" height="%d">%s</svg></body></html>'
            % (BG, -24 * pad, -24 * pad, 24 * (1 + 2 * pad), 24 * (1 + 2 * pad), px, px, GLYPH))
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "t.html")
        io.open(src, "w", encoding="utf-8").write(tile)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=%d,%d" % (px, px), "--screenshot=" + os.path.join(HERE, name), "file://" + src],
                       check=True, capture_output=True)
    print("%-22s %6d bytes" % (name, os.path.getsize(os.path.join(HERE, name))))

manifest = {
    "name": "ocr.siliconwat.dev drawings",
    "short_name": "demo.siliconwat.dev",
    "description": "Drawings of ocr.siliconwat.dev, a free reader for the Khmer Tipitaka, in English and Khmer. They read and charge nothing.",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": BG, "theme_color": ACCENT,
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
}
io.open(os.path.join(HERE, "site.webmanifest"), "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print("site.webmanifest written")
