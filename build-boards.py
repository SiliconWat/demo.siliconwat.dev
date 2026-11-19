#!/usr/bin/env python3
"""Generate the ocr.siliconwat.dev artboards and canvas.json.

    python3 build-boards.py && python3 build-index.py && python3 build-wall.py

The spec is private; these drawings follow it. The neutrals are READ from the vendored brand layer (brand.py, guarded by
scripts/check-brand.mjs); this surface's own colors are the one marked block in brand.py, filled into board.base.css.

A Silicon Wat surface: no B-Emblem and no heart anywhere (the emblem stands for the B in HeartBank), and the icon is a
PLACEHOLDER until Silicon Wat's own mark is settled. Not an H3 surface, so no not-a-chartered-bank footer.

The build refuses, in the rendered text of every board: "sign in", the regulated words, a progress figure, a countdown,
any AI model or vendor named as an author, and the heart. The Khmer is OURS and UNREVIEWED; every Khmer board says so.
The sample page is real Pali (the opening of a sutta, in Khmer script); the dictionary entry is quoted from the data that
khmer.siliconwat.dev already publishes. File names, page counts and the question asked are made up.
"""
import hashlib, io, json, os, re
from brand import fill, icon_svg, ACCENT

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, DW, DH = 390, 844, 1280, 800
CSS = io.open(os.path.join(HERE, "board.base.css"), encoding="utf-8").read()
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500'
         '&family=Noto+Sans+Khmer:wght@400;500;600&family=Noto+Serif+Khmer:wght@400;500&family=Moul&display=swap">')

BARRED = [r"\bsign[\s-]?in\b", r"\bdeposit", r"\bsavings\b", r"\binterest\b", r"\byield\b", r"\bbank\b", r"chartered",
          r"\bremaining\b", r"\bseconds? left\b", r"\bminutes? left\b", r"\bstreak", r"\brank", r"\bclaude\b", r"\bgpt", r"chatgpt",
          r"\bgemini\b", r"\bopenai\b", r"\banthropic\b", r"\bllama\b", r"\btesseract", r"\bheart\b", r"♥", r"❤"]
EMBLEM_SIG = "M3.9743 20.0257"  # the first move of the B-Emblem path: it must appear in no board

# ── the sample page: the opening of a sutta, Pali in Khmer script, as the Buddhist Institute edition prints it ──────────
PALI = ["នមោ តស្ស ភគវតោ អរហតោ សម្មាសម្ពុទ្ធស្ស ។",
        "ឯវំ មេ សុតំ ។ ឯកំ សមយំ ភគវា សាវត្ថិយំ",
        "វិហរតិ ជេតវនេ អនាថបិណ្ឌិកស្ស អារាមេ ។",
        "តត្រ ខោ ភគវា ភិក្ខូ អាមន្តេសិ ភិក្ខវោតិ ។",
        "ភទន្តេតិ តេ ភិក្ខូ ភគវតោ បច្ចស្សោសុំ ។",
        "ភគវា ឯតទវោច ។"]
ROMAN = ["namo tassa bhagavato arahato sammāsambuddhassa.",
         "evaṃ me sutaṃ. ekaṃ samayaṃ bhagavā sāvatthiyaṃ",
         "viharati jetavane anāthapiṇḍikassa ārāme.",
         "tatra kho bhagavā bhikkhū āmantesi bhikkhavoti.",
         "bhadanteti te bhikkhū bhagavato paccassosuṃ.",
         "bhagavā etadavoca."]
# Samdech Chuon Nath's entry for ជេតវន, quoted from Dictionary.json (id 3464) as khmer.siliconwat.dev serves it.
ENTRY = ("បា.(ន.) (ជេតវន  “ព្រៃរបស់ព្រះរាជកុមារជេត”) ឈ្មោះអារាមមួយធំ (ក្នុងពុទ្ធសម័យ) នៅជិតក្រុងសាវត្ថីក្នុងដែនកោសល, "
         "ដែលអនាថបិណ្ឌិកមហាសេដ្ឋី (សុទត្ត) ជាវដីជាឧទ្យានរបស់ព្រះអង្គម្ចាស់ជេតកសាងជាវត្ត ហើយវេរចំពោះព្រះភិក្ខុសង្ឃ "
         "មានព្រះសម្មាសម្ពុទ្ធជាប្រធាន; ហៅក្លាយជា ជេតពន ឬ ជេតុពន (--ពន់) ក៏មាន ។")

# ── small stroke icons (currentColor) ───────────────────────────────────────────────────────────────────────────────
def ic(d, size=16):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">%s</svg>' % (size, size, d))


SHARE = ic('<path d="M12 15V3m0 0L7 8m5-5 5 5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/>')
COPY = ic('<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>')
DOWN = ic('<path d="M12 3v12m0 0-5-5m5 5 5-5"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>')
SPEAK = ic('<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/>')
ASK = ic('<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M9.8 9.6a2.3 2.3 0 0 1 4.4.9c0 1.5-2.2 2-2.2 2M12 15.5h.01"/>')
EXT = ic('<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>')
CAM = ic('<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>')
FILE = ic('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>')
TICK = ic('<path d="M5 12.5 10 17l9-10"/>', 16).replace('stroke="currentColor"', 'stroke="%s"' % ACCENT)
DEVICE = ic('<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>', 18)


def spot(kind):
    d = {
        "page": '<rect class="sf" x="14" y="2" width="28" height="36" rx="3"/><path class="ss" d="M20 11h16M20 18h16M20 25h10"/>',
        "measure": '<rect class="sf" x="4" y="12" width="48" height="16" rx="3"/><path class="sk" d="M12 12v6M20 12v4M28 12v6M36 12v4M44 12v6"/>'
                   '<path class="ss" d="M10 33l6-5 6 3 8-7"/>',
        "device": '<rect class="sf" x="18" y="3" width="20" height="34" rx="4"/><path class="ss" d="M24 14h8M24 20h8M24 26h5"/>'
                  '<path class="sk" d="M8 20h6M42 20h6" stroke-dasharray="2 3"/>',
        "file": '<path class="sf" d="M14 3h20l8 8v26H14z"/><path class="ss" d="M20 18h16M20 25h12"/><rect class="sa" x="28" y="29" width="18" height="8" rx="4"/>',
        "voice": '<path class="sf" d="M10 15h7l8-7v24l-8-7h-7z"/><path class="ss" d="M31 14a8 8 0 0 1 0 12M36 9a15 15 0 0 1 0 22"/>',
    }[kind]
    return '<svg class="spot" width="56" height="40" viewBox="0 0 56 40" aria-hidden="true">%s</svg>' % d


def card(sp, h, *ps):
    return '<div class="card">%s<h2>%s</h2>%s</div>' % (spot(sp) if sp else "", h, "".join("<p>%s</p>" % p for p in ps))


# ── the drawn scan: HTML, so each outline fits the words it surrounds ──────────────────────────────────────────────────
def scan(states=None, cls="", extra=""):
    """states: one letter per printed line — f found · r read · c being read now · w faint (low confidence) · '' none."""
    states = states or [""] * len(PALI)
    out = ['<div class="pn">៣</div>']
    for i, (ln, s) in enumerate(zip(PALI, states)):
        wrap = ' class="c"' if i == 0 else (' class="in"' if i in (1, 3) else "")
        out.append('<div%s><span class="pl%s">%s</span></div>' % (wrap, (" " + s) if s else "", ln))
    return '<div class="scan%s" role="img" aria-label="A drawn page of Pali printed in Khmer script">%s%s</div>' % (
        (" " + cls) if cls else "", "".join(out), extra)


def thumbs(t):
    cells = []
    for n in range(10, 19):
        on = 12 <= n <= 14
        bars = "".join('<i style="width:%d%%"></i>' % w for w in (60, 100, 92, 100, 86, 100, 48)[: 5 + n % 3])
        cells.append('<div class="th%s">%s<div class="pg">%s</div><span class="n">%s</span></div>'
                     % (" on" if on else "", '<span class="ck">✓</span>' if on else "", bars, t(str(n), km_num(n))))
    return '<div class="thumbs">%s</div>' % "".join(cells)


def km_num(n):
    return str(n).translate(str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩"))


def dots():
    return '<span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>'


def leaf(t):
    return ('<div class="leaf"><span class="k">%s</span><span class="seg"><span class="on">%s</span><span>%s</span></span></div>'
            '<p class="leafnote">%s</p>' % (t("This page is in", "ទំព័រនេះជា"), t("Pāli", "បាលី"), t("Khmer", "ខ្មែរ"),
                                            t("Found by the reader. Tap the other to switch.", "ម៉ូដែលបានរកឃើញ។ ចុចមួយទៀត ដើម្បីប្តូរ។")))


def ocr(lines=PALI, rom=False, cls="", upto=None, tail=""):
    lines = list(lines)[:upto] if upto else list(lines)
    return '<div class="ocr%s%s">%s%s</div>' % (" rom" if rom else "", (" " + cls) if cls else "",
                                                "".join('<span class="ln">%s</span>' % l for l in lines), tail)


def picker(t):
    return ('<div class="card"><div class="radio on"><i></i><div><div class="t">%s <span class="lic">Apache-2.0</span></div><div class="s">%s</div></div></div>'
            '<div class="radio"><i></i><div><div class="t">%s <span class="lic">CC0</span></div><div class="s">%s</div></div></div>'
            '<p class="fine" style="margin-top:6px">%s</p></div>'
            % (t("Most accurate", "ត្រឹមត្រូវបំផុត"), t("The fewest mistakes. Chosen for you.", "កំហុសតិចបំផុត។ បានជ្រើសរើសជូនអ្នក។"),
               t("Public domain", "កម្មសិទ្ធិសាធារណៈ"), t("A few more mistakes. Its file belongs to everyone.", "កំហុសច្រើនជាងបន្តិច។ ឯកសាររបស់វាជាកម្មសិទ្ធិរបស់មនុស្សគ្រប់គ្នា។"),
               t("The license matters only if you share the model file itself.", "អាជ្ញាប័ណ្ណមានន័យ តែនៅពេលអ្នកចែករំលែកឯកសារម៉ូដែលនោះផ្ទាល់ប៉ុណ្ណោះ។")))


def privacy(t):
    return '<div class="note" style="display:flex;gap:10px;align-items:flex-start">%s<span>%s</span></div>' % (
        DEVICE, t("Your page is read on this device. It is never uploaded.", "ទំព័ររបស់អ្នកត្រូវបានអាននៅលើឧបករណ៍នេះ។ វាមិនត្រូវបានផ្ញើទៅកន្លែងណាឡើយ។"))


def drop(t, desk=False):
    big = ('<svg width="%d" height="%d" viewBox="0 0 56 40" aria-hidden="true"><rect class="sf" x="16" y="2" width="24" height="32" rx="3"/>'
           '<path class="ss" d="M22 10h12M22 16h12M22 22h8"/><path class="ss" d="M28 38V28m0 0-4 4m4-4 4 4"/></svg>') % ((84, 60) if desk else (64, 46))
    return ('<div class="drop"%s>%s<b>%s</b><span>%s</span></div><div class="btnrow"><div class="btn">%s%s</div><div class="btn ghost">%s%s</div></div>'
            % (' style="padding:56px 24px 48px"' if desk else "", big, t("Drop a page here", "ទម្លាក់ទំព័រនៅទីនេះ"),
               t("A photo, a scan or a PDF", "រូបថត ស្កេន ឬ PDF"), FILE, t("Choose a file", "ជ្រើសរើសឯកសារ"), CAM, t("Take a photo", "ថតរូប")))


# ── screens ────────────────────────────────────────────────────────────────────────────────────────────────────────
def S1(t):
    return ('<span class="tag">[ PLACEHOLDER ICON ]</span><h1>%s</h1><p class="lede">%s</p>' % (
        t("Read a page of the Tipiṭaka", "អានទំព័រមួយនៃព្រះត្រៃបិដក"),
        t("Pāli and Khmer printed in Khmer script, from the Buddhist Institute edition (1927–69). Free, and read on this device.",
          "បាលី និងខ្មែរ ដែលបោះពុម្ពជាអក្សរខ្មែរ ពីព្រះត្រៃបិដកបោះពុម្ពរបស់ពុទ្ធសាសនបណ្ឌិត្យ (១៩២៧–១៩៦៩)។ ឥតគិតថ្លៃ ហើយអាននៅលើឧបករណ៍នេះ។"))
        + drop(t) + privacy(t) + '<p class="sh">%s</p>' % t("Reader", "ម៉ូដែលអាន") + picker(t))


def S1b(t):
    return ('<h1>%s</h1><div class="file">%s<span><b>volume-12.pdf</b> · %s</span></div>' % (t("Choose pages", "ជ្រើសរើសទំព័រ"), FILE, t("486 pages", "៤៨៦ ទំព័រ"))
            + '<span class="seg" style="font-size:13px"><span>%s</span><span class="on">%s</span></span>' % (t("One page", "មួយទំព័រ"), t("A range", "ចន្លោះទំព័រ"))
            + '<div class="range"><div class="field"><span class="k">%s</span>%s</div><div class="field"><span class="k">%s</span>%s</div></div>'
            % (t("From page", "ពីទំព័រ"), t("12", "១២"), t("To page", "ដល់ទំព័រ"), t("14", "១៤"))
            + '<p class="sh">%s</p>' % t("Pages in this file", "ទំព័រក្នុងឯកសារនេះ") + thumbs(t)
            + '<p class="fine">%s</p>' % t("Pages are read in order, one at a time, on this device. A whole volume is long, so choose the pages you need.",
                                           "ទំព័រត្រូវបានអានតាមលំដាប់ ម្តងមួយទំព័រ នៅលើឧបករណ៍នេះ។ សៀវភៅមួយក្បាលវែងណាស់ ដូច្នេះសូមជ្រើសតែទំព័រដែលអ្នកត្រូវការ។")
            + '<div class="btn">%s</div><div class="btn ghost">%s</div>' % (t("Read these pages", "អានទំព័រទាំងនេះ"), t("Choose another file", "ជ្រើសឯកសារផ្សេង")))


def S2(t):
    return ('<h1>%s</h1><p class="lede">%s</p>' % (t("Getting the reader ready", "កំពុងរៀបចំម៉ូដែលអាន"),
            t("This happens once. The reader is kept in this browser, so next time it starts straight away.",
              "ការនេះកើតឡើងតែម្តង។ ម៉ូដែលត្រូវបានរក្សាទុកក្នុងកម្មវិធីរុករកនេះ ដូច្នេះលើកក្រោយវាចាប់ផ្តើមភ្លាមៗ។"))
            + scan(cls="dim") + '<p class="cap">%s</p>' % t("Your page, waiting to be read", "ទំព័ររបស់អ្នក កំពុងរង់ចាំការអាន")
            + '<div class="btn busy" role="status" aria-label="%s">%s</div>' % (t("Working", "កំពុងដំណើរការ"), dots())
            + card("device", t("Most accurate", "ត្រឹមត្រូវបំផុត"), t("It comes from this site, not from anywhere else, and your page stays on this device.",
                                                                    "វាមកពីគេហទំព័រនេះ មិនមែនពីកន្លែងផ្សេងទេ ហើយទំព័ររបស់អ្នកនៅតែលើឧបករណ៍នេះ។")))


def S3(t):
    return ('<div class="status">%s %s</div>' % (t("Reading", "កំពុងអាន"), dots()) + leaf(t)
            + scan(["r", "r", "r", "c", "f", "f"])
            + '<p class="sh">%s</p>' % t("Read so far", "បានអានរួច")
            + ocr(upto=3, tail='<span class="ln">%s</span>' % dots())
            + '<div class="btn ghost">%s</div>' % t("Stop", "បញ្ឈប់"))


def result_tools(t, rom=False):
    return ('<div class="row"><span>%s</span><span class="tog%s"></span></div>' % (t("Show in roman letters", "បង្ហាញជាអក្សរឡាតាំង"), " on" if rom else "")
            + '<div class="tools"><span class="tool">%s%s</span><span class="tool">%s%s</span></div>' % (COPY, t("Copy", "ចម្លង"), DOWN, t("Download .txt", "ទាញយក .txt"))
            + '<div class="note">%s</div>' % t("Check it against the print.", "សូមផ្ទៀងផ្ទាត់វាជាមួយសៀវភៅបោះពុម្ព។"))


def S4(t):
    return ('<h1>%s</h1>' % t("The text", "អត្ថបទ") + leaf(t) + ocr() + result_tools(t)
            + '<p class="fine">%s</p>' % t("Tap a word for its meaning. Select words to hear them or ask about them.",
                                           "ចុចលើពាក្យមួយ ដើម្បីមើលន័យ។ ជ្រើសពាក្យ ដើម្បីស្តាប់ ឬសួរអំពីវា។")
            + '<div class="btn ghost">%s</div>' % t("Read another page", "អានទំព័រផ្សេងទៀត"))


def S4r(t):
    return ('<h1>%s</h1>' % t("The text", "អត្ថបទ") + leaf(t) + ocr(ROMAN, rom=True) + result_tools(t, rom=True)
            + '<p class="fine">%s</p>' % t("Roman letters are our own transliteration, for convenience. The Khmer script is the text.",
                                           "អក្សរឡាតាំងជាការចម្លងអក្សររបស់យើង ដើម្បីភាពងាយស្រួល។ អក្សរខ្មែរគឺជាអត្ថបទ។")
            + '<div class="btn ghost">%s</div>' % t("Read another page", "អានទំព័រផ្សេងទៀត"))


def S5(t):
    helps = [t("A flat page, well lit, with no shadow across it.", "ទំព័ររាបស្មើ មានពន្លឺល្អ គ្មានស្រមោលពាក់កណ្តាល។"),
             t("The whole page in the picture, taken straight on.", "ទំព័រទាំងមូលនៅក្នុងរូប ថតត្រង់ពីលើ។"),
             t("A page of the Buddhist Institute edition (1927–69).", "ទំព័រនៃព្រះត្រៃបិដកបោះពុម្ពរបស់ពុទ្ធសាសនបណ្ឌិត្យ (១៩២៧–១៩៦៩)។")]
    return (scan(cls="tilt", extra='<div class="shade"></div>')
            + '<h1>%s</h1><p class="lede">%s</p>' % (t("No lines of text found", "រកមិនឃើញបន្ទាត់អត្ថបទទេ"),
                                                    t("The reader found no printed lines in this picture.", "ម៉ូដែលរកមិនឃើញបន្ទាត់អក្សរបោះពុម្ពក្នុងរូបនេះទេ។"))
            + '<p class="sh">%s</p><div class="card"><ul class="ticks">%s</ul></div>' % (t("What helps", "អ្វីដែលជួយបាន"), "".join("<li>%s<span>%s</span></li>" % (TICK, h) for h in helps))
            + '<p class="fine">%s</p>' % t("A scan reads best. Photos from a phone have not been measured yet.", "ស្កេនអានបានល្អបំផុត។ រូបថតពីទូរសព្ទ មិនទាន់ត្រូវបានវាស់វែងនៅឡើយទេ។")
            + '<div class="btn">%s</div>' % t("Try another page", "សាកល្បងទំព័រផ្សេង"))


def S6(t):
    return (scan(["w"] * 6, cls="other")
            + '<h1>%s</h1><p class="lede">%s</p>' % (t("This may not be the print it knows", "នេះប្រហែលមិនមែនជាអក្សរបោះពុម្ពដែលវាស្គាល់ទេ"),
                t("The reader was trained on one edition's typeface, the Buddhist Institute's Tipiṭaka (1927–69), and reads other prints poorly.",
                  "ម៉ូដែលនេះត្រូវបានបង្ហាត់លើពុម្ពអក្សរនៃការបោះពុម្ពតែមួយ គឺព្រះត្រៃបិដករបស់ពុទ្ធសាសនបណ្ឌិត្យ (១៩២៧–១៩៦៩) ហើយអានការបោះពុម្ពផ្សេងៗបានមិនល្អទេ។"))
            + '<div class="btn">%s</div><div class="btn ghost">%s</div>' % (t("Try another page", "សាកល្បងទំព័រផ្សេង"), t("Show what it read anyway", "បង្ហាញអ្វីដែលវាបានអាន")))


CREDITS = [("Transcription", "[ the transcriber's name — to come ]"),
           ("Text", "the Buddhist Institute edition of the Tipiṭaka (Phnom Penh, 1927–69)"),
           ("Scans", "Upāsikā Kang Huychan and family · Lok Kru Aggapaṇḍita But Savong · Srong Chanda · 5000-years.org, given as dhamma dāna"),
           ("Made by", "Silicon Wat℠, with Miss Aquarius℠ (AI collaboration, disclosed)")]


def S7(t):
    km = t("", "x") == "x"
    priv = ("Your images and text are read on this device and never uploaded: the page is built so that it cannot send them. "
            "Two things leave only when you press: a passage you choose to hear (to our voice service and Azure) and a passage "
            "you ask about (to the assistant you chose). Visits are counted without cookies, and the count never sees an image or a word.")
    lic = ("Most accurate: Apache-2.0. Public domain: CC0. The license matters only if you share a model file itself. "
           "The training data is not released.")
    return ('<h1>%s</h1>' % t("About and credits", "អំពី និងការទទួលស្គាល់")
            + '<div class="iconrow">%s<span class="tag">[ PLACEHOLDER ICON ] Silicon Wat\'s own mark is not settled</span></div>' % icon_svg(ACCENT, 40, "ico")
            + card("page", t("What it reads", "អ្វីដែលវាអាន"),
                   t("Pāli and Khmer printed in Khmer script: both pages of each opening of the Buddhist Institute edition of the Tipiṭaka (Phnom Penh, 1927–69). It tells which one a page is, and you can switch it.",
                     "បាលី និងខ្មែរ ដែលបោះពុម្ពជាអក្សរខ្មែរ៖ ទំព័រទាំងពីរនៃការបើកនីមួយៗ នៃព្រះត្រៃបិដកបោះពុម្ពរបស់ពុទ្ធសាសនបណ្ឌិត្យ (ភ្នំពេញ ១៩២៧–១៩៦៩)។ វាដឹងថាទំព័រនីមួយៗជាភាសាណា ហើយអ្នកអាចប្តូរវាបាន។"))
            + card("measure", t("How well it reads", "វាអានបានល្អប៉ុណ្ណា"),
                   t("On Pāli pages the models never saw, Most accurate got 1.5% of characters wrong, and Public domain 2.3%. Khmer pages: [ figure to come ].",
                     "លើទំព័របាលីដែលម៉ូដែលមិនធ្លាប់ឃើញ ត្រឹមត្រូវបំផុត ខុស ១,៥% នៃតួអក្សរ ហើយ កម្មសិទ្ធិសាធារណៈ ខុស ២,៣%។ ទំព័រខ្មែរ៖ [ តួលេខនឹងមកដល់ ]។"),
                   t("It was trained on one edition's typeface and learned from one transcriber's typing, including some of their habits. The Vinaya volumes read least well, and photos from a phone have not been measured yet.",
                     "វាត្រូវបានបង្ហាត់លើពុម្ពអក្សរនៃការបោះពុម្ពតែមួយ ហើយរៀនពីការវាយអក្សររបស់អ្នកចម្លងម្នាក់ រួមទាំងទម្លាប់ខ្លះរបស់គាត់។ ភាគវិន័យអានបានខ្សោយជាងគេ ហើយរូបថតពីទូរសព្ទមិនទាន់ត្រូវបានវាស់វែងនៅឡើយទេ។"))
            + '<div class="note">%s</div>' % t("Check what it reads against the print.", "សូមផ្ទៀងផ្ទាត់អ្វីដែលវាអាន ជាមួយសៀវភៅបោះពុម្ព។")
            + (('<p class="fine" style="margin:0 0 12px">%s</p>' % "សេចក្តីអំពីឯកជនភាព អាជ្ញាប័ណ្ណ និងការទទួលស្គាល់ ខាងក្រោមនេះ នៅជាភាសាអង់គ្លេស រហូតដល់អ្នកអានជនជាតិខ្មែរអនុម័តការបកប្រែ។") if km else "")
            + '<div lang="en">' + card("device", t("Your privacy", "ឯកជនភាពរបស់អ្នក"), priv) + card("file", t("The two readers", "ម៉ូដែលអានទាំងពីរ"), lic)
            + '<p class="sh">%s</p><div class="card"><ul class="cr">%s</ul></div></div>' % (t("Credits", "ការទទួលស្គាល់"), "".join("<li><b>%s</b>%s</li>" % c for c in CREDITS))
            + '<div class="card" style="text-align:center"><div class="pali">សព្វទានំ ធម្មទានំ ជិនាតិ</div><p>%s</p></div>'
            % t("The gift of the Dhamma surpasses every gift. Dhammapada 354", "ធម្មទាន ឈ្នះទានទាំងពួង។ ធម្មបទ ៣៥៤"))


def S8(t):
    lines = list(PALI)
    lines[2] = lines[2].replace("ជេតវនេ", '<span class="tap">ជេតវនេ</span>')
    return ('<h1>%s</h1>' % t("The text", "អត្ថបទ") + leaf(t) + ocr(lines)
            + '<div class="sheet"><div class="grab"></div><p class="sh" style="margin-top:0">%s</p><div class="head">ជេតវន</div>'
            % t("Samdech Chuon Nath's dictionary", "វចនានុក្រម សម្តេចព្រះសង្ឃរាជ ជួន ណាត")
            + '<p class="fine" style="margin-top:0">%s</p><p class="entry">%s</p>' % (
                t("You tapped ជេតវនេ. This is ជេតវន, the same word without its Pāli ending.", "អ្នកបានចុចលើ ជេតវនេ។ នេះគឺ ជេតវន ពាក្យដដែល ដោយគ្មានចុងពាក្យបាលី។"), ENTRY)
            + '<div class="legend"><span>បា. %s</span><span>ន. %s</span></div>' % (t("Pāli", "បាលី"), t("noun", "នាម"))
            + '<p class="fine">%s</p>' % t("A Khmer dictionary: it fits Khmer pages, and Pāli words that entered Khmer. When a word has no entry, it says so and never guesses.",
                                           "វចនានុក្រមខ្មែរ៖ វាសមនឹងទំព័រខ្មែរ និងពាក្យបាលីដែលចូលមកក្នុងភាសាខ្មែរ។ ពេលពាក្យមួយគ្មានក្នុងវចនានុក្រម វាប្រាប់ដូច្នោះ ហើយមិនទាយឡើយ។")
            + '<div class="btn ghost">%s</div></div>' % t("Close", "បិទ"))


def selected():
    lines = list(PALI)
    lines[1] = lines[1].replace("ឯកំ សមយំ ភគវា សាវត្ថិយំ", '<span class="sel hs">ឯកំ សមយំ ភគវា សាវត្ថិយំ</span>')
    lines[2] = '<span class="sel he">%s</span>' % lines[2]
    return lines


def S9(t):
    return ('<h1>%s</h1>' % t("The text", "អត្ថបទ") + leaf(t) + ocr(selected())
            + '<div class="bar"><span>%s%s</span><span>%s%s</span><span>%s%s</span></div>' % (
                SPEAK, t("Listen", "ស្តាប់"), ASK, t("Ask about this", "សួរអំពីនេះ"), COPY, t("Copy", "ចម្លង"))
            + '<div class="card">%s<h2>%s</h2><span class="seg" style="font-size:13px;margin:4px 0 10px"><span class="on">Sreymom · %s</span><span>Piseth · %s</span></span><p>%s</p></div>'
            % (spot("voice"), t("Khmer voice", "សំឡេងខ្មែរ"), t("woman", "ស្ត្រី"), t("man", "បុរស"),
               t("Listen sends only the words you selected to our voice service, which has Azure's Khmer voices read them aloud. Nothing is sent until you press Listen. Your image and the rest of the text stay on this device.",
                 "ស្តាប់ ផ្ញើតែពាក្យដែលអ្នកបានជ្រើស ទៅសេវាសំឡេងរបស់យើង ដែលឱ្យសំឡេងខ្មែររបស់ Azure អានឮៗ។ គ្មានអ្វីត្រូវបានផ្ញើទេ រហូតដល់អ្នកចុច ស្តាប់។ រូបភាព និងអត្ថបទផ្សេងទៀតរបស់អ្នក នៅលើឧបករណ៍នេះ។")))


def S10(t):
    opt = '<div class="radio%s"><i></i><div><div class="t">%s</div><div class="s">%s</div></div></div>'
    return ('<h1>%s</h1>' % t("The text", "អត្ថបទ") + leaf(t) + ocr(selected()) + '<div class="scrim"></div>'
            + '<div class="sheet" style="margin-top:-150px"><div class="grab"></div><h2>%s</h2><div class="quote">%s %s</div>'
            % (t("Ask about this passage", "សួរអំពីអត្ថបទនេះ"), PALI[1].split("។ ", 1)[1], PALI[2])
            + '<div class="field area"><span class="k">%s</span>%s</div>' % (t("Your question", "សំណួររបស់អ្នក"),
                                                                             t("Where was the Jetavana, and who gave it?", "តើវត្តជេតពននៅឯណា ហើយអ្នកណាជាអ្នកថ្វាយ?"))
            + '<p class="sh">%s</p><div class="card">%s%s%s%s</div>' % (t("Ask in", "សួរនៅ"),
                opt % (" on", 'Buddha AI · siliconwat.com <span class="tag">[ checked in the build ]</span>', t("From Silicon Wat℠", "ពី Silicon Wat℠")),
                opt % ("", "[ Assistant name ]", t("Opens in a new tab", "បើកក្នុងផ្ទាំងថ្មី")),
                opt % ("", "[ Assistant name ]", t("Opens in a new tab", "បើកក្នុងផ្ទាំងថ្មី")),
                opt % ("", t("Just copy it", "ចម្លងប៉ុណ្ណោះ"), t("The passage and your question, ready to paste anywhere", "អត្ថបទ និងសំណួររបស់អ្នក រួចរាល់សម្រាប់បិទភ្ជាប់គ្រប់ទីកន្លែង")))
            + '<div class="note">%s</div>' % t("AI assistants may assume a different edition's wording. Check what it says against the print.",
                                               "ជំនួយការ AI អាចសន្មតយកពាក្យពេចន៍នៃការបោះពុម្ពផ្សេង។ សូមផ្ទៀងផ្ទាត់អ្វីដែលវានិយាយ ជាមួយសៀវភៅបោះពុម្ព។")
            + '<div class="btn">%s%s</div><p class="fine">%s</p></div>' % (EXT, t("Ask", "សួរ"), t("Nothing leaves this page until you press Ask.", "គ្មានអ្វីចេញពីទំព័រនេះទេ រហូតដល់អ្នកចុច សួរ។")))


# ── desktop, English only ──────────────────────────────────────────────────────────────────────────────────────────
def D1(t):
    return ('<span class="tag">[ PLACEHOLDER ICON ]</span><div class="cols"><div><h1>%s</h1><p class="lede" style="font-size:17px">%s</p>%s%s</div>'
            % (t("Read a page of the Tipiṭaka", ""), t("Pāli and Khmer printed in Khmer script, from the Buddhist Institute edition (1927–69). Free, and read on this device.", ""),
               drop(t, desk=True), privacy(t))
            + '<div><p class="sh" style="margin-top:22px">%s</p>%s%s</div></div>' % (t("Reader", ""), picker(t),
                card("page", t("What it reads", ""), t("Both pages of each opening: the Pāli, and its Khmer translation. It tells which one a page is, and you can switch it.", ""))))


def D4(t):
    return ('<div class="cols"><div><p class="sh" style="margin-top:18px">%s</p>%s<p class="cap">%s</p></div>'
            % (t("Your page", ""), scan(["r"] * 6).replace('class="scan"', 'class="scan" style="font-size:19px;padding:14px 30px 20px"'),
               t("The lines it found are outlined. Check the text against them.", ""))
            + '<div><h1>%s</h1>%s%s%s<p class="fine">%s</p><div class="btn ghost" style="width:auto;display:inline-block;padding:12px 22px">%s</div></div></div>'
            % (t("The text", ""), leaf(t), ocr(), result_tools(t),
               t("Click a word for its meaning. Select words to hear them or ask about them.", ""), t("Read another page", "")))


SCREENS = [
    ("1", "Empty", S1), ("1b", "PDF page chooser", S1b), ("2", "First use: getting the reader ready", S2), ("3", "Reading", S3),
    ("4", "Result", S4), ("4r", "Result, roman letters on", S4r), ("5", "No lines found", S5), ("6", "Not this print", S6),
    ("7", "About and credits", S7), ("8", "A word's dictionary entry", S8), ("9", "A passage selected: Listen, Ask", S9),
    ("10", "The Ask panel", S10),
]
NOFOOT = {"8", "10"}


def page(sid, render, lang, dark=False, desk=False):
    km = lang == "km"
    t = (lambda e, k: k) if km else (lambda e, k: e)
    body = render(t).replace("℠", '<span class="sm">℠</span>')
    plain = re.sub(r"<[^>]+>", " ", body)
    for pat in BARRED + ([r"ធនាគារ"] if km else []):
        assert not re.search(pat, plain, re.I), "%s/%s: barred %r" % (sid, lang, pat)
    if sid != "7":
        assert not re.search(r"\d\s*%|[០-៩]\s*%", plain), "%s/%s: a percentage outside About (a progress figure?)" % (sid, lang)
    assert EMBLEM_SIG not in body, "%s: the B-Emblem path is in a Silicon Wat board" % sid
    band = ("Khmer: our draft, not yet reviewed · ភាសាខ្មែរ៖ សេចក្តីព្រាងរបស់យើង មិនទាន់បានពិនិត្យ" if km else "")
    themes = "".join('<span%s>%s</span>' % (' class="on"' if i == (2 if dark else 0) else "", x) for i, x in enumerate(t(("System", "Light", "Dark"), ("ប្រព័ន្ធ", "ភ្លឺ", "ងងឹត"))))
    langs = "".join('<span%s>%s</span>' % (' class="on"' if (i == 0) == (not km) else "", x) for i, x in enumerate(("EN", "ខ្មែរ")))
    foot = '<footer><span><a>%s</a> · %s</span><span class="seg">%s</span></footer>' % (
        t("About and credits", "អំពី និងការទទួលស្គាល់"), t("Visits are counted without cookies.", "ការចូលមើលត្រូវបានរាប់ដោយគ្មានខូគី។"), themes)
    share = '<span class="sharebtn" aria-label="%s">%s</span>' % (t("Share", "ចែករំលែក"), SHARE)
    cls = " ".join(c for c in (lang, "dark" if dark else "", "desk" if desk else "") if c)
    return """<!doctype html>
<html lang="%s" class="%s">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=%d">
<meta name="googlebot" content="noindex,nofollow"><meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow"><meta name="yandex" content="noindex,nofollow">
<title>ocr.siliconwat.dev drawings · %s</title>
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<style>[hidden]{display:none!important}</style>
%s
<link rel="stylesheet" href="board.css?v=@CSSV@">
</head>
<body>
%s<div class="app">
<header><span class="hl">%s<span class="wm">ocr.siliconwat.dev</span></span><span class="hr"><span class="seg">%s</span>%s</span></header>
%s
%s
</div>
</body>
</html>
""" % (lang, cls, DW if desk else W, sid, FONTS, '<div class="band">%s</div>' % band if band else "", icon_svg(ACCENT, 26), langs, share, body,
       "" if sid in NOFOOT else '<div class="grow"></div>' + foot)


def main():
    css = fill(CSS)
    io.open(os.path.join(HERE, "board.css"), "w", encoding="utf-8").write(css)
    cssv = hashlib.sha256(css.encode()).hexdigest()[:8]
    hpath = os.path.join(HERE, "heights.json")
    hts = json.load(io.open(hpath)) if os.path.exists(hpath) else {}
    hh = lambda f, base=H: max(base, int(hts.get(f, base)))
    tall = lambda sfx: max([H] + [int(v) for k, v in hts.items() if k.endswith(sfx) and not k.startswith("D")])
    pages = [{"id": "ocr", "name": "ocr.siliconwat.dev"}]
    boards = []
    y_km = tall(".html") + 160
    for i, (sid, title, render) in enumerate(SCREENS):
        for lang, y in (("en", 0), ("km", y_km)):
            f = "S%s%s.html" % (sid, "" if lang == "en" else "Km")
            io.open(os.path.join(HERE, f), "w", encoding="utf-8").write(page(sid, render, lang).replace("@CSSV@", cssv))
            boards.append({"file": f, "page": "ocr", "title": "%s · %s, %s, phone" % (sid, title, "English" if lang == "en" else "Khmer"),
                           "w": W, "h": hh(f), "x": i * (W + 80), "y": y})
    y3 = y_km + max([H] + [int(v) for k, v in hts.items() if k.endswith("Km.html")]) + 160
    x = 0
    for f, sid, render, title, dark, desk in (("D1.html", "1", D1, "1 · Empty, English, desktop", False, True),
                                               ("D4.html", "4", D4, "4 · Result, English, desktop", False, True),
                                               ("S1Dark.html", "1", S1, "1 · Empty, dark pass, English, phone", True, False),
                                               ("S4Dark.html", "4", S4, "4 · Result, dark pass, English, phone", True, False)):
        io.open(os.path.join(HERE, f), "w", encoding="utf-8").write(page(sid, render, "en", dark=dark, desk=desk).replace("@CSSV@", cssv))
        w = DW if desk else W
        boards.append({"file": f, "page": "ocr", "title": title, "w": w, "h": hh(f, DH if desk else H), "x": x, "y": y3})
        x += w + 80
    canvas = {"pages": pages, "artboards": boards, "annotations": [], "launch": {"page": "ocr", "view": "canvas"}}
    io.open(os.path.join(HERE, "canvas.json"), "w", encoding="utf-8").write(json.dumps(canvas, ensure_ascii=False, indent=1))
    print("%d artboards written · board.css v=%s" % (len(boards), cssv))


if __name__ == "__main__":
    main()
