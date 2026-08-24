#!/usr/bin/env python3
"""Rip the essential data out of the big interactive Adams chart and store
it compactly.

    python3 extract.py [SOURCE.html] [-o chart.json]

The source (kyle/toys/bpc4_h1_adams_chart.html) embeds a 277KB `DATA`
object whose bulk is human-readable class labels and seed strings. A
spectral-sequence *picture* needs almost none of that — only:

  • where the classes sit (stem x, filtration y),
  • what kind of group each is (Z square / Z/2 dot / Z/4 ring),
  • the differentials (which page, from where, to where).

We drop labels, seeds, and the per-page recomputed cell lists (keeping just
the base page E_3, which carries every class), and emit:

  {
    "title": str, "base_page": 3, "max_stem": int, "max_filt": int,
    "legend": {"s":"Z","d":"Z/2","o":"Z/4"},
    "nodes": [[x, y, "ods"], ...],     # one string per cell; one char per
                                       # generator: s=square d=dot o=open
    "diffs": [[r, sx, sy, tx, ty], ...]
  }

That's a faithful, compact chart you can window and restyle freely.
"""

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_SRC = HERE.parent.parent / "kyle" / "toys" / "bpc4_h1_adams_chart.html"

# group name -> marker code (mnemonic: square / dot / open ring)
CODE = {"Z": "s", "Z2": "d", "Z4": "o"}


def load_data(src):
    txt = Path(src).read_text()
    m = re.search(r"const DATA = (\{.*?\});", txt, re.S)
    if not m:
        raise SystemExit(f"could not find `const DATA = …` in {src}")
    return json.loads(m.group(1))


def page_nodes(page):
    nodes = []
    for c in sorted(page["cells"], key=lambda c: (c["x"], c["y"])):
        codes = "".join(CODE.get(g, "d") for g in c["groups"])
        nodes.append([c["x"], c["y"], codes])
    return nodes


def extract(data, start=5):
    # Emit EVERY page from E_{start} onward, each with its own surviving
    # classes and the d_r differentials that live on it, so the chart can be
    # paged through: E_5 (all d5), E_7 (d7), ... E_inf (none). Starting at E_5
    # (not E_3) means d_3 has already collapsed the multi-class bidegrees, so
    # each spot carries a single class and the chart reads clean. A class's
    # group can change page to page (e.g. Z/4 -> Z/2), which the markers show.
    by_num = {p.get("page"): p for p in data["pages"]}
    nums = sorted(n for n in by_num if n >= start)   # e.g. 5, 7, 11, 13, 99
    arrows = sorted(data["arrows"], key=lambda a: (a["page"], a["s"]))

    pages = []
    for r in nums:
        diffs = [[a["page"], a["s"][0], a["s"][1], a["t"][0], a["t"][1]]
                 for a in arrows if a["page"] == r]      # d_r on this page
        pages.append({"r": r, "nodes": page_nodes(by_num[r]), "diffs": diffs})
    return {
        "title": data.get("title", ""),
        "start": start,
        "max_stem": data.get("max_stem"),
        "max_filt": data.get("max_filt"),
        "legend": {"s": "Z", "d": "Z/2", "o": "Z/4"},
        "pages": pages,
    }


def embed_in_html(json_text, html_path=HERE / "chart.html"):
    """Inline the chart data into chart.html's <script id="chart-data"> block,
    so the chart also renders straight from file:// with no server (a bare
    fetch() is blocked there). Keeping this in sync here means one command,
    `python3 extract.py`, updates both chart.json and chart.html."""
    html = Path(html_path).read_text()
    pat = re.compile(
        r'(<script id="chart-data" type="application/json">)(.*?)(</script>)',
        re.S,
    )
    if not pat.search(html):
        print(f"  (no <script id=\"chart-data\"> block in {Path(html_path).name}; "
              "skipped inlining)")
        return
    # never let a literal </script> inside the JSON close the tag early
    safe = json_text.replace("</", "<\\/")
    html = pat.sub(lambda m: f"{m.group(1)}\n{safe.strip()}\n{m.group(3)}", html)
    Path(html_path).write_text(html)
    print(f"  inlined data into {Path(html_path).name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", default=str(DEFAULT_SRC))
    ap.add_argument("-o", "--out", default=str(HERE / "chart.json"))
    ap.add_argument("-p", "--page", type=int, default=5,
                    help="first E-page to include (default 5)")
    args = ap.parse_args()

    out = extract(load_data(args.source), start=args.page)
    # one line per page keeps the generated file readable + diff-friendly
    c = lambda v: json.dumps(v, separators=(",", ":"))
    page_lines = []
    for p in out["pages"]:
        nodes = ",".join(c(n) for n in p["nodes"])
        diffs = ",".join(c(d) for d in p["diffs"])
        page_lines.append(f'    {{"r":{p["r"]},"nodes":[{nodes}],"diffs":[{diffs}]}}')
    text = (
        "{\n"
        f'  "title": {json.dumps(out["title"])},\n'
        f'  "start": {out["start"]},\n'
        f'  "max_stem": {out["max_stem"]},\n'
        f'  "max_filt": {out["max_filt"]},\n'
        f'  "legend": {json.dumps(out["legend"])},\n'
        '  "pages": [\n'
        + ",\n".join(page_lines)
        + "\n  ]\n}\n"
    )
    Path(args.out).write_text(text)
    embed_in_html(text)

    print(f"wrote {args.out}  "
          f"({Path(args.out).stat().st_size / 1024:.1f} KB, "
          f"source was {Path(args.source).stat().st_size / 1024:.0f} KB)")
    for p in out["pages"]:
        label = "E_inf" if p["r"] == 99 else f"E_{p['r']}"
        print(f"  {label:6s} {len(p['nodes']):3d} cells, {len(p['diffs']):3d} differentials")


if __name__ == "__main__":
    main()
