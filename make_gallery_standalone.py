#!/usr/bin/env python3
"""Wrap the Steenrod-module gallery into a standalone, shareable HTML file.

    python3 make_gallery_standalone.py   ->  steenrod-modules.html

steenrod-gallery.partial.html is the gallery on its own (style + grid + a
self-contained click-to-copy script) and normally gets included into the site's
fun page. This script wraps that same partial in a minimal HTML shell with its
own theme tokens and a tiny dark-mode toggle — no nav, no site CSS, no fonts,
no other page text — so the result is a single file you can send to anyone.

Re-run this after regenerating steenrod-gallery.partial.html.
"""

from pathlib import Path

ROOT = Path(__file__).parent
PARTIAL = ROOT / "steenrod-gallery.partial.html"
OUT = ROOT / "steenrod-modules.html"

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Steenrod modules</title>
<!-- Standalone, self-contained gallery of Steenrod modules. Generated from
     steenrod-gallery.partial.html by make_gallery_standalone.py. No external
     assets: open it anywhere, or send it as a single file. -->
<style>
  :root{
    color-scheme: light;
    --paper:#FFFFFF; --ink:#000000; --rule:#DCDCDC; --accent:#1E66F5;
    --wide:74rem; --s5:1.5rem;
    --font-mono:'Roboto Mono', ui-monospace, Menlo, monospace;
  }
  :root[data-theme='dark']{
    color-scheme: dark;
    --paper:#2E3440; --ink:#ECEFF4; --rule:#434C5E; --accent:#88C0D0;
  }
  html,body{ margin:0; background:var(--paper); color:var(--ink);
    font-family:var(--font-mono); }
  body{ padding-block:2.5rem 3rem; -webkit-font-smoothing:antialiased; }
  /* tiny, unobtrusive light/dark toggle, top-right */
  .theme-toggle{
    position:fixed; top:.7rem; right:.8rem; z-index:20;
    font:500 .7rem/1 var(--font-mono); letter-spacing:.08em; text-transform:lowercase;
    color:var(--ink); background:var(--paper);
    border:1px solid var(--rule); border-radius:999px;
    padding:.4rem .8rem; cursor:pointer; opacity:.65;
    transition:opacity .15s ease, border-color .15s ease;
  }
  .theme-toggle:hover{ opacity:1; border-color:var(--accent); }
</style>
</head>
<body>
<button class="theme-toggle" type="button" aria-label="Toggle dark mode">dark</button>
"""

TAIL = """
<script>
  (function () {
    var btn = document.querySelector('.theme-toggle'), root = document.documentElement;
    function sync() { btn.textContent = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; }
    btn.addEventListener('click', function () {
      if (root.getAttribute('data-theme') === 'dark') root.removeAttribute('data-theme');
      else root.setAttribute('data-theme', 'dark');
      sync();
    });
    sync();
  })();
</script>
</body>
</html>
"""


def main():
    if not PARTIAL.exists():
        raise SystemExit(f"error: {PARTIAL.name} not found")
    OUT.write_text(HEAD + PARTIAL.read_text() + TAIL)
    print(f"wrote {OUT.name} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
