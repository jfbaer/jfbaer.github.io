#!/usr/bin/env python3
"""Self-host a Google font so the published site makes no third-party
requests (Kyle's privacy principle).

    python3 vendor_font.py "Font Name" ["Another Font" ...]
    python3 vendor_font.py "Fraunces" --weights 400,500,600 --no-italic

For each family it downloads the woff2 files into fonts/, appends the
matching @font-face rules to fonts/fonts.css, and prints the line to drop
into style.md (font-serif: / font-mono:). Then run `python3 build.py`.

Browse and preview fonts first with font-lab.html; this tool is how you
keep the one you picked. Stdlib only (urllib).
"""

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
FONTS_DIR = ROOT / "fonts"
FONTS_CSS = FONTS_DIR / "fonts.css"
CSS2 = "https://fonts.googleapis.com/css2"
# A modern UA makes Google Fonts serve woff2 rather than legacy ttf.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

FACE_RE = re.compile(r"@font-face\s*\{[^}]*\}", re.S)
URL_RE = re.compile(r"url\((https://[^)]+\.woff2)\)")


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch_css(family, weight, italic):
    ital = 1 if italic else 0
    spec = f"{family.replace(' ', '+')}:ital,wght@{ital},{weight}"
    url = f"{CSS2}?family={spec}&display=swap"
    try:
        return fetch(url).decode("utf-8")
    except urllib.error.HTTPError:
        return None  # that weight/style doesn't exist for this family


def vendor(family, weights, italics):
    slug = slugify(family)
    blocks, n = [], 0
    for weight in weights:
        for italic in italics:
            css = fetch_css(family, weight, italic)
            if not css:
                continue
            style = "italic" if italic else "normal"
            for face in FACE_RE.findall(css):
                url = URL_RE.search(face)
                if not url:
                    continue
                fname = f"{slug}-{weight}-{style}-{n}.woff2"
                (FONTS_DIR / fname).write_bytes(fetch(url.group(1)))
                blocks.append(URL_RE.sub(f"url({fname})", face, count=1))
                n += 1
    if not blocks:
        sys.exit(f"error: no woff2 found for '{family}' — check the exact "
                 f"name at fonts.google.com")

    header = f"\n/* ---- Vendored by vendor_font.py: {family} ---- */\n"
    with FONTS_CSS.open("a") as f:
        f.write(header + "\n".join(blocks) + "\n")

    print(f"✓ {family}: {n} woff2 file(s) -> fonts/, {len(blocks)} @font-face "
          f"rule(s) -> fonts/fonts.css")
    print(f"  now set in style.md:  font-serif: '{family}', Georgia, serif")
    print(f"                   or:  font-mono:  '{family}', monospace")


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        sys.exit(__doc__)
    weights = ["400", "500"]
    italics = [False, True]
    families = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--weights":
            i += 1
            weights = [w.strip() for w in args[i].split(",") if w.strip()]
        elif a == "--no-italic":
            italics = [False]
        else:
            families.append(a)
        i += 1
    if not families:
        sys.exit("error: name at least one font family")
    for fam in families:
        vendor(fam, weights, italics)
    print("\nRun `python3 build.py` to pick up the change.")


if __name__ == "__main__":
    main()
