#!/usr/bin/env python3
"""Build the site from markdown.

    style.md     ->  styles.css   (design tokens compiled onto base.css)
    content.md   ->  index.html   (the homepage)
    pages/*.md   ->  *.html       (one standalone page per file)

Usage:  python3 build.py

No dependencies beyond the Python standard library. The look lives in
style.md (colours, fonts, spacing — light/dark pairs), the structure in
base.css, and the words in content.md. See README.md for the formats.
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
STYLE = ROOT / "style.md"
CONTENT = ROOT / "content.md"
BASE_CSS = ROOT / "base.css"
PAGES_DIR = ROOT / "pages"
TEMPLATE = ROOT / "template.html"
STYLES_OUT = ROOT / "styles.css"

GENERATED_BANNER = (
    "<!-- GENERATED FILE — do not edit. Edit {source} and run"
    " `python3 build.py`. -->"
)


# ---------------------------------------------------------------- frontmatter

def parse_frontmatter(text):
    """Split a file into (meta dict, body). Frontmatter is `key: value`
    lines between two `---` lines at the top of the file."""
    meta = {}
    if text.startswith("---"):
        try:
            end = text.index("\n---", 3)
        except ValueError:
            raise ValueError(
                "frontmatter starts with --- but has no closing --- line"
            ) from None
        meta = parse_kv(text[3:end])
        body = text[end + 4 :]
    else:
        body = text
    return meta, body.strip()


def parse_kv(block):
    """`key: value` lines -> dict. `#` lines and prose are ignored."""
    d = {}
    for line in block.strip().splitlines():
        line = line.strip()
        if line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        # keys are identifiers (token names / entry keys); skip prose that
        # merely contains a colon, so style.md comments can't leak in.
        if not re.fullmatch(r"[A-Za-z0-9_-]+", key):
            continue
        d[key] = value.strip()
    return d


# -------------------------------------------------------------------- styles

def compile_styles(tokens):
    """style.md tokens -> a :root token block prepended onto base.css.

    A key ending in `-light`/`-dark` is a theme pair: its base name gets
    the light value in :root and the dark value under [data-theme=dark].
    Any other key is a single value emitted once."""
    pairs, singles = {}, {}
    for key, val in tokens.items():
        if key.endswith("-light"):
            pairs.setdefault(key[:-6], {})["light"] = val
        elif key.endswith("-dark"):
            pairs.setdefault(key[:-5], {})["dark"] = val
        else:
            singles[key] = val

    light_lines = [f"  --{k}: {v};" for k, v in singles.items()]
    light_lines += [
        f"  --{base}: {v['light']};" for base, v in pairs.items() if "light" in v
    ]
    dark_lines = [
        f"  --{base}: {v['dark']};" for base, v in pairs.items() if "dark" in v
    ]

    root = ":root {\n  color-scheme: light;\n" + "\n".join(light_lines) + "\n}"
    dark = (
        ":root[data-theme='dark'] {\n  color-scheme: dark;\n"
        + "\n".join(dark_lines)
        + "\n}"
    )
    banner = GENERATED_BANNER.format(source="style.md").replace("<!--", "/*").replace("-->", "*/")
    return f"{banner}\n\n{root}\n\n{dark}\n\n{BASE_CSS.read_text()}"


# ------------------------------------------------------------------ math

MATH_PLACEHOLDER = "\x00MATH{}\x00"


def protect_math(text):
    """Pull $$…$$ and $…$ out before markdown mangles them; return
    (text_with_placeholders, [raw_snippets]). KaTeX renders them in the
    browser, so we keep the delimiters and just HTML-escape the inside."""
    snippets = []

    def stash(m):
        snippets.append(m.group(0))
        return MATH_PLACEHOLDER.format(len(snippets) - 1)

    # display first, then inline; ignore escaped \$
    text = re.sub(r"(?<!\\)\$\$(.+?)\$\$", stash, text, flags=re.S)
    text = re.sub(r"(?<!\\)\$(?!\s)(.+?)(?<!\s)\$", stash, text)
    return text, snippets


def restore_math(html_text, snippets):
    for i, raw in enumerate(snippets):
        opened = raw.startswith("$$")
        delim = "$$" if opened else "$"
        inner = raw[len(delim):-len(delim)]
        restored = f"{delim}{html.escape(inner, quote=False)}{delim}"
        html_text = html_text.replace(MATH_PLACEHOLDER.format(i), restored)
    return html_text


# ------------------------------------------------------------ markdown subset

def md_inline(s):
    """Inline markdown: images, links, bold, italics, code. Raw HTML
    passes through untouched."""
    s = re.sub(
        r"!\[([^\]]*)\]\(([^)\s]+)\)",
        r'<img src="\2" alt="\1" loading="lazy">',
        s,
    )
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


# block-level raw HTML (figures, embeds, generated animations) passes
# through verbatim instead of being wrapped in <p> — so you can drop in
# an <iframe class="viz">, a <figure>, a <video>, or hand-written SVG.
RAW_HTML_BLOCK = re.compile(
    r"^<(figure|iframe|img|video|audio|canvas|svg|div|section|table|pre|script|style|p)\b",
    re.I,
)


def md_blocks(body):
    """Block-level markdown: paragraphs, ### headings, - lists, > quotes,
    and raw HTML blocks (passed through untouched)."""
    html_out = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        if RAW_HTML_BLOCK.match(block):
            html_out.append(block)
        elif block.startswith("### "):
            html_out.append(f"<h3>{md_inline(block[4:])}</h3>")
        elif all(line.startswith("> ") for line in block.splitlines()):
            inner = " ".join(line[2:] for line in block.splitlines())
            html_out.append(f"<blockquote><p>{md_inline(inner)}</p></blockquote>")
        elif all(line.startswith("- ") for line in block.splitlines()):
            items = "\n".join(
                f"  <li>{md_inline(line[2:])}</li>" for line in block.splitlines()
            )
            html_out.append(f"<ul>\n{items}\n</ul>")
        else:
            html_out.append(f"<p>\n  {md_inline(block)}\n</p>")
    return "\n".join(html_out)


def slugify(title):
    """Section id from its title: 'About me' -> 'about-me'."""
    title = re.sub(r"<[^>]+>", "", title)
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


# ------------------------------------------------------------------ rendering

def render_identity(meta):
    contact = "<br>\n        ".join(
        md_inline(part.strip()) for part in meta.get("contact", "").split("|") if part.strip()
    )
    subtitle = meta.get("subtitle", "")
    parts = ['<header class="identity">', f'  <h1>{md_inline(meta["name"])}</h1>']
    if subtitle:
        parts.append(f'  <p class="subtitle">{md_inline(subtitle)}</p>')
    if contact:
        parts.append(f'  <p class="contact label">\n        {contact}\n      </p>')
    parts.append("</header>")
    return "\n      ".join(parts)


def render_page_header(site, title):
    # No back-link: the nav brand (top-left) already links home, so a second
    # copy of the name here is redundant.
    return (
        '<header class="identity">\n'
        f'      <h1>{md_inline(title)}</h1>\n'
        "      </header>"
    )


def render_nav(meta, current):
    """Build the top nav from `nav:` (pipe-separated `Label target`),
    plus the brand and the (hidden until JS) theme toggle."""
    name = meta.get("name", "Home")
    items = [f'<span class="brand label"><a href="index.html">{md_inline(name)}</a></span>']
    for part in meta.get("nav", "").split("|"):
        part = part.strip()
        if not part:
            continue
        label, _, target = part.rpartition(" ")
        label, target = (label.strip() or target), target.strip()
        cur = ' aria-current="page"' if target == current else ""
        items.append(f'<a class="label" href="{target}"{cur}>{md_inline(label)}</a>')
    items.append(
        '<button class="theme-toggle label" type="button" hidden>dark</button>'
    )
    return "\n      " + "\n      ".join(items)


def render_footer(meta):
    parts = [md_inline(p.strip()) for p in meta.get("footer", "").split("|") if p.strip()]
    if not parts:
        return ""
    sep = '<span class="sep label">·</span>'
    return "\n      " + f"\n      {sep}\n      ".join(
        f'<span class="label">{p}</span>' for p in parts
    )


def render_entry(entry):
    """One publication/preprint <article> from a key: value block."""
    if "title" not in entry:
        raise ValueError(
            f"entry block has no 'title:' line (keys found: {list(entry)})"
        )
    lines = ['<article class="entry">']
    lines.append(f'      <h3 class="entry-title">{md_inline(entry["title"])}</h3>')
    if "authors" in entry:
        lines.append(f'      <p class="entry-authors">{md_inline(entry["authors"])}</p>')
    m = " · ".join(v for v in (entry.get("year"), entry.get("status")) if v)
    if m:
        lines.append(f'      <p class="entry-meta">{m}</p>')
    links = [
        f'<a href="{entry[key]}">{label}</a>'
        for key, label in (("arxiv", "arXiv"), ("doi", "DOI"), ("pdf", "PDF"))
        if key in entry
    ]
    if "links" in entry:
        links.append(md_inline(entry["links"]))
    if links:
        lines.append(f'      <p class="entry-links">{" · ".join(links)}</p>')
    lines.append("      </article>")
    return "\n".join(lines)


ENTRIES_MARKER = re.compile(r"^<!--\s*(?:type:\s*)?entries\s*-->\s*", re.I)


def render_section(heading, body):
    """One `## Heading` section. `## [Title](url)` links the header as a
    rule-label; the trailing rule comes from base.css."""
    m = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", heading)
    title, href = (m.group(1), m.group(2)) if m else (heading, None)
    label = f'<a href="{href}">{md_inline(title)}</a>' if href else md_inline(title)
    section_id = slugify(title)

    marker = ENTRIES_MARKER.match(body)
    if marker:
        body = body[marker.end() :]
        entries = [
            render_entry(entry)
            for block in re.split(r"\n---+\n", body)
            if (entry := parse_kv(block))
        ]
        inner = "\n\n      ".join(entries)
    else:
        inner = md_blocks(body).replace("\n", "\n      ")

    return (
        f'<section id="{section_id}">\n'
        f'      <h2 class="rule-label"><span class="label">{label}</span></h2>\n'
        f"      {inner}\n"
        "    </section>"
    )


def split_sections(body):
    """Split a document body on `## ` headings -> (preamble, [(heading, body)])."""
    parts = re.split(r"(?m)^## +(.+)$", body)
    preamble = parts[0].strip()
    sections = [
        (parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts), 2)
    ]
    return preamble, sections


def render_document(header_html, body, source_name):
    parts = [GENERATED_BANNER.format(source=source_name), header_html]
    preamble, sections = split_sections(body)
    if preamble:
        parts.append(md_blocks(preamble).replace("\n", "\n    "))
    parts.extend(render_section(h, b) for h, b in sections)
    return "\n\n    ".join(parts)


# ---------------------------------------------------------------- math assets

KATEX_HEAD = '  <link rel="stylesheet" href="vendor/katex/katex.min.css">'
KATEX_BODY = """  <script defer src="vendor/katex/katex.min.js"></script>
  <script defer src="vendor/katex/auto-render.min.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', function () {
      renderMathInElement(document.getElementById('main'), {
        delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '$',  right: '$',  display: false}
        ],
        throwOnError: false
      });
    });
  </script>"""


# ------------------------------------------------------------------ assembly

def write_html(out_path, title, description, nav, content, footer, has_math):
    tpl = TEMPLATE.read_text()
    tpl = tpl.replace("{{title}}", title)
    tpl = tpl.replace("{{description}}", html.escape(description, quote=True))
    tpl = tpl.replace("{{head_extra}}", KATEX_HEAD if has_math else "")
    tpl = tpl.replace("{{nav}}", nav)
    tpl = tpl.replace("{{content}}", "    " + content)
    tpl = tpl.replace("{{footer}}", footer)
    tpl = tpl.replace("{{body_scripts}}", KATEX_BODY if has_math else "")
    out_path.write_text(tpl)
    print(f"wrote {out_path.relative_to(ROOT)}")


INCLUDE_RE = re.compile(r"^[ \t]*<!--\s*include:\s*(\S+)\s*-->[ \t]*$", re.M)


def expand_includes(body):
    """Replace `<!-- include: path -->` lines with the file's raw contents
    (relative to the project root). Lets generated partials — e.g. the
    homepage shape rail — live in their own file instead of cluttering
    content.md. The inlined HTML then flows through as a raw block."""
    def sub(m):
        p = ROOT / m.group(1)
        if not p.exists():
            raise SystemExit(f"include not found: {m.group(1)}")
        return p.read_text()
    return INCLUDE_RE.sub(sub, body)


def build_page(out_path, title, description, header_html, body, source_name,
               site, current):
    body = expand_includes(body)
    body, math = protect_math(body)
    content = render_document(header_html, body, source_name)
    content = restore_math(content, math)
    nav = render_nav(site, current)
    footer = render_footer(site)
    write_html(out_path, title, description, nav, content, footer, bool(math))


# ---------------------------------------------------------------------- build

def build():
    for required in (STYLE, CONTENT, BASE_CSS, TEMPLATE):
        if not required.exists():
            sys.exit(f"error: {required.name} not found")

    # 1. compile the design system
    tokens, _ = parse_frontmatter(STYLE.read_text())
    STYLES_OUT.write_text(compile_styles(tokens))
    print("wrote styles.css")

    # 2. homepage
    site, body = parse_frontmatter(CONTENT.read_text())
    build_page(
        ROOT / "index.html",
        site.get("name", "Home"),
        site.get("description", ""),
        render_identity(site),
        body,
        "content.md",
        site,
        "index.html",
    )

    # 3. standalone pages (inherit site nav/footer; own title/description)
    for path in sorted(PAGES_DIR.glob("*.md")) if PAGES_DIR.is_dir() else []:
        meta, page_body = parse_frontmatter(path.read_text())
        title = meta.get("title", path.stem.replace("-", " ").title())
        build_page(
            ROOT / f"{path.stem}.html",
            f"{title} — {site.get('name', '')}",
            meta.get("description", site.get("description", "")),
            render_page_header(site, title),
            page_body,
            f"pages/{path.name}",
            site,
            f"{path.stem}.html",
        )


if __name__ == "__main__":
    build()
