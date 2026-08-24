# Build spec: a personal math site in the style of e-infinity.space

Reverse-engineered from the actual source. Ormsby publishes the site from a
public repo — `github.com/kyleormsby/kyleormsby.github.io`, with `CNAME`
containing `e-infinity.space` — so none of this is guesswork. It also ships a
586-line README that documents most design decisions and the reasoning behind
them. Read that first; it is unusually good.

---

## 1. Stack at a glance

| Layer | Choice |
|---|---|
| Generator | **Astro 7**, `output: static`, `build.format: 'directory'`, `trailingSlash: 'always'` |
| Math | `remark-math` + `rehype-katex`, **rendered to HTML at build time** |
| Type | Newsreader Variable (serif) + IBM Plex Mono, self-hosted via `@fontsource` |
| Interactive work | Hand-written HTML/JS in `public/`, three.js **vendored locally** |
| Host | GitHub Pages, deployed by GitHub Actions on push to `main` |
| Tests | Playwright-driven checks for math, theme, and contrast |

Dependencies are deliberately tiny — seven runtime packages total. No React, no
Tailwind, no UI library, no CSS framework.

---

## 2. The design system

This is the part you're reacting to. It is about 400 lines of hand-written CSS
in `src/styles/global.css`, and it rests on five decisions.

### 2.1 Paper and ink, never white and black

Every colour is declared exactly once, as a `-light`/`-dark` pair, then mapped
into semantic names. There is no second copy of the palette to drift.

```css
:root {
  --paper-light:      #FCFBF8;   --paper-dark:      #121213;
  --paper-sunk-light: #F4F1E9;   --paper-sunk-dark: #191919;
  --ink-light:        #14130F;   --ink-dark:        #EDEAE2;
  --muted-light:      #5A574D;   --muted-dark:      #918C7E;
  --rule-light:       #E3DFD4;   --rule-dark:       #2B2B28;
  --accent-light:     #A93B1B;   --accent-dark:     #E8734A;
  --accent-bg-light:  #F5E9E3;   --accent-bg-dark:  #241A16;

  color-scheme: light;
  --paper: var(--paper-light);
  --ink:   var(--ink-light);
  /* …and so on */
}

:root[data-theme='dark'] {
  color-scheme: dark;
  --paper: var(--paper-dark);
  --ink:   var(--ink-dark);
}
```

Seven tokens is the whole palette. Warm off-white paper, near-black warm ink,
one terracotta accent. The restraint is doing most of the work.

### 2.2 Two typefaces with strictly divided jobs

- **Newsreader** (variable serif) — all body copy and *all headings*, at
  `font-weight: 400`. Headings scale by size and negative tracking
  (`letter-spacing: -0.015em`), never by weight. Nothing on the site is bold.
- **IBM Plex Mono** — only ever as `.label`.

The `.label` class is the workhorse of the entire design: nav, dates, tags,
section markers, footer, the theme switch.

```css
.label {
  font-family: var(--mono);
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: lowercase;      /* lowercase, not uppercase */
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
```

Lowercase-and-tracked rather than uppercase-and-tracked is a large part of the
voice. Body text also sets `font-variant-numeric: oldstyle-nums`, so numerals
sit in the line rather than shouting from it.

### 2.3 Links as animated gradient underlines

No `text-decoration` anywhere. Links are a 1px background gradient that thickens
to 2px on hover:

```css
a {
  color: inherit;
  text-decoration: none;
  background-image: linear-gradient(var(--accent), var(--accent));
  background-size: 100% 1px;
  background-repeat: no-repeat;
  background-position: 0 calc(100% - 0.08em);
  transition: background-size 0.18s ease, color 0.18s ease;
}
a:hover { color: var(--accent); background-size: 100% 2px; }
a.plain { background-image: none; }
```

The underline sits slightly above the baseline so descenders clear it.

### 2.4 One spacing scale, two widths

```css
--s1: .25rem; --s2: .5rem; --s3: .75rem; --s4: 1rem;
--s5: 1.5rem; --s6: 2rem;  --s7: 3rem;   --s8: 4.5rem; --s9: 7rem;

--measure: 66ch;   /* prose column */
--wide:    74rem;  /* gallery / schedule breakout */
```

Two layout primitives consume them:

```css
.wrap  { width: min(100% - 2.5rem, var(--wide));    margin-inline: auto; }
.prose { width: min(100% - 2.5rem, var(--measure)); margin-inline: auto; }
```

The `Base` layout takes a `wide` prop that picks between them. That's the whole
layout system.

### 2.5 A section-header pattern worth stealing

The rule that trails off after a label:

```css
.rule-label { display: flex; align-items: center; gap: var(--s4);
              margin-block: var(--s8) var(--s5); }
.rule-label::after { content: ''; flex: 1; height: 1px; background: var(--rule); }
```

Used as `<h2 class="rule-label"><span class="label">featured visualizations</span></h2>`.

Also: body size is fluid (`clamp(1.05rem, 0.98rem + 0.3vw, 1.18rem)`),
`line-height: 1.62`, and headings use `text-wrap: balance` with ledes on
`text-wrap: pretty`.

---

## 3. Dark mode without a flash

Two decisions, both worth copying verbatim.

**Light is the default outright.** `prefers-color-scheme` is *never* consulted.
Two states, no `auto`. The site is designed light; dark is an option behind a
switch.

**The choice is applied before first paint** by an inline `is:inline` script in
`<head>` that reads `localStorage` and sets `data-theme` on `<html>`. It's
written in ES5 with `try`/`catch` around storage access, because it runs before
anything else and must not throw in a private window or an embedded webview.

```html
<script is:inline>
  (function () {
    var KEY = 'theme';                 // 'dark' when chosen; absent = light
    var root = document.documentElement;
    try {
      if (localStorage.getItem(KEY) === 'dark') root.dataset.theme = 'dark';
    } catch (e) { /* private mode: stay light */ }

    window.__theme = {
      isDark: function () { return root.dataset.theme === 'dark'; },
      set: function (dark) { /* set/remove attr + storage, then: */
        document.dispatchEvent(new CustomEvent('themechange'));
      },
    };
  })();
</script>
```

The toggle button ships `hidden` and is un-hidden by the deferred script, so
it never appears to no-JS visitors as a dead control. The canvas motif can't
inherit CSS variables, so it subscribes to that `themechange` event and repaints.

---

## 4. Why it feels snappy

Nothing exotic — just a stack of subtractions:

1. **Static HTML.** Astro ships zero JS by default; there is no hydration, no
   framework runtime, no client-side router.
2. **Math is pre-rendered.** `rehype-katex` runs with `output: 'html'` at build
   time, so pages ship *no math engine* — just KaTeX's stylesheet and spans.
   This is the single biggest win over MathJax-in-the-browser, which is what
   most math sites do.
3. **Fonts are self-hosted and subset by weight** — the variable serif plus
   exactly two mono weights (400, 500). No render-blocking third-party request.
4. **One small CSS file**, ~400 lines, no framework.
5. **Total JS on a content page** is the inline theme script plus a ~10-line
   toggle handler.
6. **Images**: thumbnails are real screenshots committed as PNGs at fixed
   1200×900, with `loading="lazy"` and explicit `width`/`height` so nothing
   reflows.

Non-obvious detail: past class meetings dim and the current one is anchored at
*read* time, not build time, so schedule pages stay honest between deploys
without needing a rebuild.

---

## 5. Security — worth correcting your premise

I looked specifically for this, and I want to be straight with you: **the site
sets no security headers at all.** No CSP, no `X-Frame-Options`, no
`Referrer-Policy`, no `Permissions-Policy`. There is no meta CSP either. That
isn't an oversight so much as a constraint — GitHub Pages doesn't let you set
response headers, so a Pages-hosted site *cannot* have them.

What the site actually has is better described as **a very small attack
surface**, which is a real and underrated security property:

- **Fully static.** No server, no database, no auth, no user input, no
  server-side code to exploit.
- **Zero third-party requests.** This is the deliberate part, and it's the most
  copyable idea here. The visualizations used to pull three.js from three
  different CDNs in two versions, and two pages pulled webfonts from
  `fonts.googleapis.com`. Both are now vendored locally. The README is explicit
  that this was as much a privacy fix as a reliability one — the font requests
  disclosed every reader's IP address to a third party. I grepped the whole
  `public/` tree: **zero** references to cdnjs, unpkg, jsdelivr, or Google
  Fonts remain.
- **No analytics, no trackers, no cookies.** The only client-side storage is a
  single `theme` key in `localStorage`.
- **Supply chain kept honest.** `npm ci` against a committed lockfile in CI, and
  a `vendor:check` script that greps for CDN hostnames and fails the build if
  any reappear. The vendoring script walks the three.js addon import graph so
  only the 14 reachable modules ship, not the whole 33 MB package.
- **Least-privilege CI.** The deploy workflow declares `contents: read`,
  `pages: write`, `id-token: write` and uses OIDC via `deploy-pages@v4` — no
  long-lived deploy token.

**If you want the headers too**, host on Cloudflare Pages or Netlify instead of
GitHub Pages. Same Astro build, same repo, but you get a `_headers` file and can
set a real CSP. Given you'd be shipping interactive canvas/WebGL work, a
reasonable starting policy is `default-src 'self'`, `img-src 'self' data:`, and
`script-src 'self' 'unsafe-inline'` — the last because of that pre-paint theme
script, which you could instead hash and allow explicitly.

---

## 6. The QA harness (the genuinely unusual part)

Most personal sites have no tests. This one has four, chained as `npm run check`,
which exits non-zero on the first failure:

| Script | What it catches |
|---|---|
| `check:math` | Parses all math spans with KaTeX in **strict** mode. The build uses `strict: false` so one bad formula can't fail a deploy — which also means errors scroll past unnoticed. This fails loudly instead. Currently 497 spans, 0 rejected. |
| `check:theme` | Reads `data-theme` at *navigation commit*, before first paint. Exists to catch the silent failure where the toggle keeps working but the pre-paint script stops, so dark-mode visitors get a frame of light on every load — invisible to a screenshot taken after load. |
| `check:contrast` | Every text colour, both schemes, against WCAG AA. |
| `vendor:check` | Greps for CDN hostnames; fails if any reappear. |

The contrast check has the best lesson in the repo. It folds in **every
ancestor's `opacity`** before measuring, because a colour can pass on its own
and fail in place. That's how these were found:

| Element | Was | Now |
|---|---|---|
| `.sep` (the ❦ between links) | **1.29:1** — used `--rule`, a hairline colour, as text | uses `--muted` |
| Past meetings, mono labels | **2.97:1** — `--muted` under `opacity: 0.72` | 5.16:1 |
| `--muted-light` on its own | 5.22:1 | **7:1** (`#5A574D`) |

It also waits out the 0.18s link colour transition before reading, or it catches
every `<a>` mid-transition against an already-switched background and reports
dozens of failures that don't exist.

---

## 7. Content architecture

```
src/
  styles/global.css        design tokens — start here
  layouts/Base.astro       shell: head, nav, footer, theme script
  components/Motif.astro   the landing-page canvas animation
  lib/csv.ts               small CSV reader, no dependencies
  lib/courses.ts           CSV rows -> rendered class meetings
  lib/markup.ts            tiny markdown + KaTeX renderer for strings in JSON
  data/courses/            <course>.csv + <course>.json
  data/research.json       67 items across six sections
  content/viz/             one markdown file per visualization
  content/writing/         posts
  pages/
    index.astro
    [course]/index.astro   /113/, /544/, … generated from data/courses/
    viz/index.astro, writing/, research/, teaching/, rss.xml.ts
public/                    visualizations, verbatim, at their original URLs
tools/                     importers, screenshot scripts, checks
```

Three ideas here are worth lifting:

**Course pages are data, not code.** Each course is a CSV (one row per meeting)
plus a JSON with metadata and a **render spec** declaring how *that course's*
columns become lines:

```json
"render": [
  { "col": "topic",   "kind": "md" },
  { "col": "reading", "kind": "md",  "label": "reading", "pages": "pages" },
  { "col": "notes",   "kind": "pdf", "label": "notes",   "text": "notes" },
  { "col": "recording", "kind": "panopto", "label": "recording" }
]
```

`kind` is one of `md`, `text`, `pdf` (a file stem → `{filesBase}stem.pdf`),
`url`, or `panopto` (a bare GUID → full URL). Cells hold **stems and GUIDs, not
paths and URLs** — prefixes live once in the JSON, which keeps the CSV readable
in a spreadsheet. Adding a column to one course is a JSON edit, not a code
change. Eight courses with genuinely different shapes share one renderer.

**A course can live elsewhere.** Give its JSON an `href` and it still appears in
"currently teaching" and the index, but every link points at the real site and
**no local page is built** — no half-filled duplicate to drift out of date.

**Old URLs never break.** `astro.config.mjs` carries a `redirects` block mapping
every Jekyll and academicpages URL (`/posts/2021/11/aha/`, `/publications/`,
`/about/`) to its new home.

**Guard rails against silent failure.** `thumb` is required by the content
schema *and* its file existence is checked at build time, because a missing
thumbnail otherwise builds clean and just shows an empty frame.

---

## 8. A build plan for your site

1. `npm create astro@latest` — empty template, TypeScript, no integrations.
2. Add `remark-math`, `rehype-katex`, `katex`; configure the markdown processor
   with `output: 'html'` so math is build-time only. Set `site`,
   `trailingSlash: 'always'`, `build.format: 'directory'`.
3. Install fonts via `@fontsource` and import them in your base layout. Pick two
   faces with divided jobs — one text face, one mono for labels.
4. Write `global.css` tokens first: paired light/dark colours mapped to semantic
   names, one spacing scale, `--measure` and `--wide`. Resist adding an eighth
   colour.
5. Build `Base.astro` with the pre-paint inline theme script, skip link, nav
   with `aria-current`, and the `wide` prop.
6. Set up content collections for writing and visualizations, with a schema that
   requires a thumbnail.
7. Add the checks early — `check:math` and `check:contrast` especially. They're
   cheap now and annoying to retrofit.
8. Deploy: if you want security headers, use Cloudflare Pages rather than GitHub
   Pages. Otherwise the Actions workflow in this repo is ~30 lines and copyable
   as-is.

Two things to skip unless you need them: the 668 MB `public/files/` archive
(GitHub Pages caps at 1 GB, and the README documents a painful Ghostscript
compression pass to get under it), and the course CSV system unless you actually
teach.

---

## 9. One caveat

The repo is public but has **no LICENSE file**, which by default means all
rights reserved. Lifting the architecture, the token approach, the pre-paint
theme trick, and the check scripts is completely normal engineering practice —
those are techniques, and several are documented in the README as lessons. But
don't copy `global.css` or the motif component wholesale and call it done.

Since he's your undergraduate advisor, the easy move is just to email him. In my
experience someone who writes a 586-line README explaining *why* he chose
`{\square\mkern-11mu\diagup}` for a lifting-property operator is going to be
delighted that you read it.
