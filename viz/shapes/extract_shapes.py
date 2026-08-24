#!/usr/bin/env python3
"""Rip three specific little shapes out of the big sequential128 chart set
and emit them as clean, mutually-aligned SVGs for the homepage rail.

    python3 extract_shapes.py

Source: kyle/toys/sequential128.html — 128 stem-charts, each stored in a
<template id="chart-N"> as plain SVG (<circle> nodes, <line> edges) on a
60px lattice. The displayed chart applies scale(1,-1), so larger cy is
higher filtration; we bake that flip in here.

A "shape" is a full visual cluster: we compute connected components of the
node/edge graph, then group components that sit within ~1.5 lattice steps
of each other. (The green infinite-family row is its own component in the
data — no edge joins it to the lower-left diamond — but it sits one step
below, so proximity grouping folds it in, as intended.) The three wanted:

  1. chart-33, the MIDDLE cluster of three
  2. chart-32, the LOWER-LEFT-most cluster   (diamond + blue + green row)
  3. chart-32, the UPPER-RIGHT-most cluster

Each is re-based to its own local frame (min corner → 0) so the three can
be stacked and centered as a matched set — identical lattice unit, node
radius and stroke across all three. Colours (blue towers, red edges, green
family, black default) are preserved as CSS classes driven by variables,
so size and palette are a one-line change later.

Outputs (in this dir):
  shapes.json        the ripped geometry, local frames, lattice units
  rail.html          self-contained standalone preview (open in a browser)
  rail.partial.html  just <style>+<div> — paste/включить into the homepage
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE.parent.parent / "kyle" / "toys" / "sequential128.html"
UNIT = 60.0  # px per lattice step in the source

SNAP = 2.0          # px tolerance matching an edge endpoint to a node
GROUP_GAP = 1.5     # merge components whose bboxes are within this many units

# (label, chart template id, selector)  selector picks a grouped cluster:
#   "middle"                  -> the median cluster by centroid x
#   "lowerleft"               -> min centroid (x + y)
#   "upperright"              -> max centroid (x + y)
#   "upperright-of-lowerleft" -> nearest cluster strictly up-and-right of
#                                the lower-left one (its diagonal neighbour)
#
# Two selectable variants of the left-hand rail; pick with `--set a|b`.
SETS = {
    # A: the middle diamond, then chart-32's lower-left (incl. green row)
    #    and upper-right clusters.
    "a": [
        ("diamond-33-mid", "chart-33", "middle"),
        ("lower-left-32",  "chart-32", "lowerleft"),
        ("upper-right-32", "chart-32", "upperright"),
    ],
    # B: the same middle diamond, then chart-36's lower-left cluster and the
    #    shape immediately to its upper right.
    "b": [
        ("diamond-33-mid",    "chart-33", "middle"),
        ("lower-left-36",     "chart-36", "lowerleft"),
        ("upper-right-nbr-36", "chart-36", "upperright-of-lowerleft"),
    ],
}

LINE_TAG = re.compile(r'<line\b[^>]*>')
CIRC_TAG = re.compile(r'<circle\b[^>]*>')
COORDS = re.compile(
    r'x1="([-\d.]+)"\s+y1="([-\d.]+)"\s+x2="([-\d.]+)"\s+y2="([-\d.]+)"')
CXY = re.compile(r'cx="([-\d.]+)"\s+cy="([-\d.]+)"')


def template_body(text, tid):
    m = re.search(rf'<template id="{tid}">(.*?)</template>', text, re.S)
    if not m:
        raise SystemExit(f"template {tid} not found")
    return m.group(1)


def colour(style):
    s = (style or "").lower()
    for c in ("blue", "red", "green"):
        if c in s:
            return c
    return "ink"


def _find(parent, i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def _union(parent, a, b):
    parent[_find(parent, a)] = _find(parent, b)


def nearest_node(nodes, x, y):
    for i, n in enumerate(nodes):
        if abs(n['x'] - x) < SNAP and abs(n['y'] - y) < SNAP:
            return i
    return None


def connected_components(nodes, edges):
    """Union-find over nodes joined by an edge (endpoints snapped to nodes).
    Returns a list of node-index sets."""
    parent = list(range(len(nodes)))
    for e in edges:
        a = nearest_node(nodes, e['x1'], e['y1'])
        b = nearest_node(nodes, e['x2'], e['y2'])
        if a is not None and b is not None:
            _union(parent, a, b)
    groups = {}
    for i in range(len(nodes)):
        groups.setdefault(_find(parent, i), set()).add(i)
    return list(groups.values())


def bbox(nodes, idxs):
    xs = [nodes[i]['x'] for i in idxs]
    ys = [nodes[i]['y'] for i in idxs]
    return min(xs), min(ys), max(xs), max(ys)


def group_by_proximity(nodes, comps, gap):
    """Merge components whose bounding boxes lie within `gap` lattice units
    of each other (in both axes) — folds the green row into its diamond."""
    g = gap * UNIT
    boxes = [bbox(nodes, c) for c in comps]
    parent = list(range(len(comps)))
    for i in range(len(comps)):
        for j in range(i + 1, len(comps)):
            ax0, ay0, ax1, ay1 = boxes[i]
            bx0, by0, bx1, by1 = boxes[j]
            sepx = max(0, max(ax0, bx0) - min(ax1, bx1))
            sepy = max(0, max(ay0, by0) - min(ay1, by1))
            if sepx <= g and sepy <= g:
                _union(parent, i, j)
    merged = {}
    for i, c in enumerate(comps):
        merged.setdefault(_find(parent, i), set()).update(c)
    return list(merged.values())


def shapes_of(text, tid):
    """All grouped clusters in a chart, each as (edges, nodes) it contains."""
    edges, nodes = parse_template(text, tid)
    comps = group_by_proximity(nodes, connected_components(nodes, edges), GROUP_GAP)
    out = []
    for members in comps:
        pts = {(round(nodes[i]['x'], 1), round(nodes[i]['y'], 1)) for i in members}
        m_nodes = [nodes[i] for i in members]
        # an edge belongs to the cluster if either endpoint lands on its nodes
        # (keeps the green family's left arrow, which ends in empty space)
        m_edges = [e for e in edges
                   if (round(e['x1'], 1), round(e['y1'], 1)) in pts
                   or (round(e['x2'], 1), round(e['y2'], 1)) in pts]
        cx = sum(n['x'] for n in m_nodes) / len(m_nodes) / UNIT
        cy = sum(n['y'] for n in m_nodes) / len(m_nodes) / UNIT
        out.append(dict(edges=m_edges, nodes=m_nodes, cx=cx, cy=cy))
    return out


def select(clusters, how):
    if how == "middle":
        return sorted(clusters, key=lambda c: c['cx'])[len(clusters) // 2]
    if how == "lowerleft":
        return min(clusters, key=lambda c: c['cx'] + c['cy'])
    if how == "upperright":
        return max(clusters, key=lambda c: c['cx'] + c['cy'])
    if how == "upperright-of-lowerleft":
        L = min(clusters, key=lambda c: c['cx'] + c['cy'])
        up_right = [c for c in clusters
                    if c['cx'] > L['cx'] + 0.5 and c['cy'] > L['cy'] + 0.5]
        if not up_right:
            raise SystemExit("no upper-right neighbour of the lower-left shape")
        return min(up_right,
                   key=lambda c: (c['cx'] - L['cx'])**2 + (c['cy'] - L['cy'])**2)
    raise SystemExit(f"unknown selector {how!r}")


def parse_template(text, tid):
    """Parse whole <line>/<circle> tags, then read coords + colour from each
    tag string. Robust to attribute order (style may precede or follow)."""
    body = template_body(text, tid)
    edges, nodes = [], []
    for tag in LINE_TAG.findall(body):
        m = COORDS.search(tag)
        if not m:
            continue
        x1, y1, x2, y2 = map(float, m.groups())
        edges.append(dict(x1=x1, y1=y1, x2=x2, y2=y2,
                          c=colour(tag), arrow="marker-end" in tag))
    for tag in CIRC_TAG.findall(body):
        m = CXY.search(tag)
        if not m:
            continue
        nodes.append(dict(x=float(m.group(1)), y=float(m.group(2)), c=colour(tag)))
    return edges, nodes


def rebase(cluster):
    """Re-base a selected cluster to its own local frame (min corner -> 0),
    flipping y so larger filtration is up."""
    sel_nodes, sel_edges = cluster['nodes'], cluster['edges']
    xs = [n['x'] for n in sel_nodes] + [e[k] for e in sel_edges for k in ('x1', 'x2')]
    ys = [n['y'] for n in sel_nodes] + [e[k] for e in sel_edges for k in ('y1', 'y2')]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)

    def lx(x): return round((x - minx) / UNIT, 4)
    def ly(y): return round((maxy - y) / UNIT, 4)   # flip: larger cy -> top

    return {
        "w": round((maxx - minx) / UNIT, 4),
        "h": round((maxy - miny) / UNIT, 4),
        "nodes": [[lx(n['x']), ly(n['y']), n['c']] for n in sel_nodes],
        "edges": [[lx(e['x1']), ly(e['y1']), lx(e['x2']), ly(e['y2']), e['c'],
                   1 if e['arrow'] else 0] for e in sel_edges],
    }


def separate_coincident(shape, gap=0.5):
    """A bidegree with two classes overlaps once the nodes are enlarged. Rather
    than pull the two nodes apart (which stretches every edge touching them),
    shift each node's whole *diamond* — its ink-connected component — as a rigid
    unit: the upper diamond left, the lower one right. Internal edges keep their
    shape; only the long differential (red/blue) edges to off-diamond towers
    flex slightly, which is invisible. Generalises to any doubled bidegree."""
    from collections import defaultdict
    nodes, edges = shape["nodes"], shape["edges"]

    def nearest(x, y):                            # edge endpoint -> node index
        for i, (nx, ny, _) in enumerate(nodes):
            if abs(nx - x) < 0.03 and abs(ny - y) < 0.03:
                return i
        return None

    emap = [(nearest(e[0], e[1]), nearest(e[2], e[3])) for e in edges]

    parent = list(range(len(nodes)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for e, (ia, ib) in zip(edges, emap):          # union nodes joined by ink
        if e[4] == "ink" and ia is not None and ib is not None:
            parent[find(ia)] = find(ib)
    comp = defaultdict(list)
    for i in range(len(nodes)):
        comp[find(i)].append(i)

    cells = defaultdict(list)
    for i, (x, y, _) in enumerate(nodes):
        cells[(round(x), round(y))].append(i)

    off = [0.0] * len(nodes)
    moved = False
    for idxs in cells.values():
        if len(idxs) < 2:
            continue
        roots = [find(i) for i in idxs]
        if len(set(roots)) != len(roots):
            continue                              # share a component: can't split
        cy = {r: sum(nodes[j][1] for j in comp[r]) / len(comp[r]) for r in roots}
        # SVG y grows downward, so the top-of-image diamond has the SMALLER y.
        order = sorted(idxs, key=lambda i: cy[find(i)])    # top of image first
        k = len(order)
        for m, i in enumerate(order):
            delta = (m - (k - 1) / 2) * gap       # top -> left, bottom -> right
            for j in comp[find(i)]:
                off[j] += delta
        moved = True
    if not moved:
        return shape

    for i in range(len(nodes)):
        nodes[i][0] = round(nodes[i][0] + off[i], 4)
    for e, (ia, ib) in zip(edges, emap):          # re-anchor edges to moved nodes
        if ia is not None:
            e[0], e[1] = nodes[ia][0], nodes[ia][1]
        if ib is not None:
            e[2], e[3] = nodes[ib][0], nodes[ib][1]

    xs = [n[0] for n in nodes] + [e[k] for e in edges for k in (0, 2)]
    ys = [n[1] for n in nodes] + [e[k] for e in edges for k in (1, 3)]
    shift = min(xs)
    if shift:                                     # keep the frame starting at 0
        for n in nodes:
            n[0] = round(n[0] - shift, 4)
        for e in edges:
            e[0] = round(e[0] - shift, 4); e[2] = round(e[2] - shift, 4)
    shape["w"] = round(max(xs) - shift, 4)
    shape["h"] = round(max(ys) - min(ys), 4)
    return shape


# ------------------------------------------------------------------ SVG

STYLE = """<style>
  /* Homepage shape rail — generated by viz/shapes/extract_shapes.py.
     SIZE and PALETTE are deliberately just the variables below, so they
     are a one-line change once the owner gives guidance. POSITION is a
     fixed left-margin column on wide screens (hidden where the prose would
     collide — the responsive story is still TBD). */
  .sq-rail{
    /* --- tune these later --- */
    --sq-unit: 28px;                 /* px per lattice step (overall size)  */
    --sq-node-r: 0.17;               /* node radius, in lattice units       */
    --sq-edge-w: 0.13;               /* edge stroke width, in lattice units */
    --sq-ink:   #000000;             /* default (black) classes             */
    --sq-blue:  #1e66f5;             /* blue towers                         */
    --sq-red:   #d20f39;             /* red edges                           */
    --sq-green: #40a02b;             /* green family                        */
    /* centred in the left margin: span from the page edge to the prose, so
       align-items:center puts each shape exactly midway between the two. */
    position: fixed;
    left: 0; width: calc((100vw - var(--measure)) / 2);
    top: 50%; transform: translateY(-50%);
    display: flex; flex-direction: column; align-items: center; gap: 1.9rem;
    z-index: 1; pointer-events: none;
  }
  @media (max-width: 1100px){ .sq-rail{ display: none; } }  /* TBD: small screens */
  /* dark mode: black diamonds -> cream, accent colours brightened to read
     on the dark paper. */
  [data-theme='dark'] .sq-rail{
    --sq-ink:   #eceff4;
    --sq-blue:  #81a1c1;
    --sq-red:   #bf616a;
    --sq-green: #a3be8c;
  }
  .sq-rail svg{ display: block; overflow: visible;
                shape-rendering: geometricPrecision; }
  .sq-c-ink  { --c: var(--sq-ink);   }
  .sq-c-blue { --c: var(--sq-blue);  }
  .sq-c-red  { --c: var(--sq-red);   }
  .sq-c-green{ --c: var(--sq-green); }
  .sq-n{ fill: var(--c); r: var(--sq-node-r); }
  .sq-e{ stroke: var(--c); fill: none; stroke-width: var(--sq-edge-w);
         stroke-linecap: round; stroke-linejoin: round; }
  .sq-caption{
    max-width: 13rem; margin-top: .7rem;
    font-family: var(--font-mono); font-size: .64rem; line-height: 1.5;
    letter-spacing: .02em; text-align: center; color: var(--muted);
  }
  .sq-caption .katex{ font-size: 1em; }
</style>"""

# Caption under the rail. Inline $…$ math renders via KaTeX on the homepage
# (build.py detects the math and loads KaTeX); the standalone preview shows
# the raw TeX, which is fine.
CAPTION = r"motifs in the $v_1$-periodic unstable stems"


def shape_svg(label, s, pad=0.55):
    # Centre the viewBox horizontally on the black-node (diamond) centroid, not
    # the bounding box, so the diamonds line up vertically across the stacked
    # shapes even when towers extend farther on one side.
    ink_xs = [n[0] for n in s["nodes"] if n[2] == "ink"] or [n[0] for n in s["nodes"]]
    cx = sum(ink_xs) / len(ink_xs)
    half = max(cx, s["w"] - cx) + pad
    vx, W = cx - half, 2 * half
    H = s["h"] + 2 * pad
    parts = [
        f'<svg class="sq-shape" data-shape="{label}" role="img" '
        f'aria-label="{label}" '
        f'viewBox="{vx:.3f} {-pad:.3f} {W:.3f} {H:.3f}" '
        f'style="width:calc(var(--sq-unit) * {W:.3f}); '
        f'height:calc(var(--sq-unit) * {H:.3f})">',
        '  <defs><marker id="sq-arrow-%s" orient="auto" markerUnits="userSpaceOnUse" '
        'markerWidth="0.6" markerHeight="0.6" refX="0.5" refY="0.3">'
        '<path d="M0,0 L0,0.6 L0.5,0.3 Z" fill="context-stroke"/></marker></defs>'
        % label,
    ]
    for x1, y1, x2, y2, c, arrow in s["edges"]:
        mk = f' marker-end="url(#sq-arrow-{label})"' if arrow else ""
        parts.append(f'  <line class="sq-e sq-c-{c}" x1="{x1}" y1="{y1}" '
                     f'x2="{x2}" y2="{y2}"{mk}/>')
    for x, y, c in s["nodes"]:
        parts.append(f'  <circle class="sq-n sq-c-{c}" cx="{x}" cy="{y}"/>')
    parts.append('</svg>')
    return "\n".join(parts)


def build_rail(shapes):
    svgs = "\n".join(shape_svg(lbl, shapes[lbl]) for lbl in shapes)
    cap = f'\n  <div class="sq-caption">{CAPTION}</div>' if CAPTION else ""
    partial = f'{STYLE}\n<div class="sq-rail">\n{svgs}{cap}\n</div>\n'
    standalone = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<title>homepage shapes — preview</title>'
        '<style>body{margin:0;background:#FCFBF8;min-height:100vh;'
        'display:flex;align-items:center;padding:2rem}</style></head>'
        f'<body>\n{partial}</body></html>\n'
    )
    return partial, standalone


def build_set(text, name):
    shapes = {}
    for lbl, tid, how in SETS[name]:
        shapes[lbl] = separate_coincident(rebase(select(shapes_of(text, tid), how)))
    return shapes


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", choices=sorted(SETS), default="a",
                    help="which variant to wire into the homepage (default a)")
    active = ap.parse_args().set

    text = SRC.read_text()
    for name in sorted(SETS):
        shapes = build_set(text, name)
        partial, standalone = build_rail(shapes)
        # per-set files, always regenerated so both can be previewed
        (HERE / f"shapes-{name}.json").write_text(json.dumps(shapes, indent=2))
        (HERE / f"rail-{name}.partial.html").write_text(partial)
        (HERE / f"rail-{name}.html").write_text(standalone)
        # the active set is also written to the plain names the homepage uses
        if name == active:
            (HERE / "shapes.json").write_text(json.dumps(shapes, indent=2))
            (HERE / "rail.partial.html").write_text(partial)
            (HERE / "rail.html").write_text(standalone)
        mark = "  <- active (homepage)" if name == active else ""
        print(f"set {name}:{mark}")
        for lbl, s in shapes.items():
            print(f"  {lbl:20s} {len(s['nodes']):2d} nodes, {len(s['edges']):2d} edges, "
                  f"{s['w']:.0f}×{s['h']:.0f} units")


if __name__ == "__main__":
    main()
