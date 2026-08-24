# Academic Website — Build Spec

A spec for building a simple, single-page academic website in the style of
[hassanabdallah.com](https://hassanabdallah.com/), using the **Eldritch** color
theme and hosted on **GitHub Pages**. Hand this file to Claude Code as the source
of truth for implementation.

---

## 1. Overview

- **Type:** Single-page, static academic homepage. No build step, no framework.
- **Goal:** Minimal, fast, readable. A narrow single column of content on a dark
  eldritch background. Sections stacked vertically: header/identity → About →
  Publications → Preprints. Links out to arXiv / DOI / a hosted CV PDF.
- **Audience:** Academics, collaborators, hiring committees. Prioritize clarity
  and load speed over interactivity.
- **Non-goals:** No blog engine, no CMS, no JavaScript framework, no analytics,
  no cookie banners. Plain HTML + CSS. A tiny bit of vanilla JS is acceptable
  only if genuinely needed (e.g. a light/dark toggle — optional, see §9).

---

## 2. Tech stack & constraints

- **HTML5 + CSS3 only.** One `index.html`, one `styles.css`. Uses the system font
  Times New Roman — no web fonts to load (see §4).
- **No external JS dependencies.** No jQuery, no bundlers.
- Must work with **GitHub Pages** served from the repo root (see §10).
- All paths **relative** (e.g. `files/cv.pdf`, not `/files/cv.pdf`) so it works
  both at `username.github.io` and `username.github.io/repo-name/`.
- Mobile-first and responsive (see §7).
- Semantic HTML: use `<header>`, `<main>`, `<section>`, `<article>`, `<h1>`–`<h3>`,
  `<nav>` if a nav is added. No `<div>` soup.

---

## 3. Color theme — Eldritch

Dark, Lovecraftian palette (indigo base, green/cyan/purple accents). Define these
as CSS custom properties on `:root` and use them everywhere — never hardcode hex
in rules.

```css
:root {
  --bg:            #212337;  /* page background (main indigo) */
  --bg-elevated:   #282a36;  /* cards, header bar, code blocks */
  --bg-deep:       #171928;  /* header image well, deepest surface */
  --border:        #323449;  /* hairlines, dividers, selection */
  --fg:            #ebfafa;  /* primary body text */
  --muted:         #7081d0;  /* secondary text, contact info, meta lines */
  --green:         #37f499;  /* name / primary accent */
  --cyan:          #04d1f9;  /* links, section headings */
  --purple:        #a48cf2;  /* subtitle / secondary accent */
  --red:           #f16c75;  /* rare emphasis / hover states */
  --orange:        #f7c67f;  /* publication titles / highlights */
  --yellow:        #f1fc79;  /* sparingly, if at all */
}
```

**Usage guidance:**
- Page `background: var(--bg)`; body text `color: var(--fg)`.
- **Name / your identity heading:** `var(--green)`.
- **Subtitle** (e.g. "Ph.D. Candidate in X"): `var(--purple)`.
- **Section headings** ("About me", "Publications"): `var(--cyan)`.
- **Links:** `var(--cyan)` default; on hover, `var(--green)` with `text-decoration:
  underline`. Visited links may stay cyan (don't dim them).
- **Publication / preprint titles:** `var(--orange)`.
- **Author lists, dates, venue, contact lines:** `var(--muted)`.
- **Your own name inside author lists:** bold + `var(--fg)` so it stands out.
- Keep it restrained: two or three accents doing most of the work. Green for
  identity, cyan for structure + links, orange for titles. Red/yellow are spice.

Contrast: `--fg` on `--bg` and all accent colors on `--bg` pass WCAG AA. Do **not**
put `--muted` (#7081d0) on `--bg` at small sizes for anything critical — it's fine
for meta text but not body copy.

---

## 4. Typography

**Times New Roman throughout.** It's a system font, so **no Google Fonts, no
`<link>`, nothing to load** — hosting stays trivial and the page renders instantly.
Define a single serif stack:

```css
:root {
  --font-body: 'Times New Roman', Times, serif;
}
```

Use `--font-body` for everything — name, headings, body, contact, and meta. There
is no separate heading or mono font; differentiation comes from **size, weight, and
the eldritch accent colors** (§3), not from a second typeface.

Note on rendering: Times New Roman ships on virtually all Windows and macOS
machines and will render natively there. On the rare Linux/mobile device without
it, the `Times`/`serif` fallbacks give a near-identical serif — acceptable and
expected. (If you ever want *pixel-identical* rendering everywhere, the Google Font
**Tinos** is a metric-compatible Times clone you could swap in later, but it is
**not** required and not part of this build.)

**Type scale (rem-based):**
- Name (`h1`): 1.9–2.1rem, bold, `--green`.
- Subtitle: 1rem, `--purple`.
- Section headings (`h2`): 1.2rem, bold, `--cyan`.
- Body: 1rem, `line-height: 1.7`.
- Contact + meta: 0.9rem, `--muted`.

---

## 5. Page structure & content model

Single column. Suggested max content width **720px**, centered, with generous
horizontal padding on mobile. Order of sections:

### 5.1 Header / identity
- Optional header image well (`--bg-deep` background). In the reference it's a
  fractal; use a placeholder `files/header.png` and let the user swap it. If no
  image is provided, omit the well gracefully.
- **Name** (`h1`, `--green`).
- **Subtitle** line (`--purple`): role + field, e.g. "Ph.D. Candidate in
  Mathematics".
- **Contact block** (`--muted`): email (obfuscated as
  `you [at] university [dot] edu` to reduce scraping), office/room, optionally
  links to Google Scholar / GitHub / ORCID.

### 5.2 About me
- `h2` "About me" (`--cyan`).
- One or two short paragraphs of prose. Inline links to institutions/advisors in
  `--cyan`.
- A line linking to the CV: `My CV can be found <a href="files/cv.pdf">here</a>.`

### 5.3 Publications
- `h2` "Publications" (`--cyan`).
- A list of entries. **Each entry** (`<article>` or `<li>`):
  - **Title** — bold, `--orange`.
  - **Author line** — `--muted`; the site owner's name **bold + `--fg`**.
  - **Year, venue** — `--muted`.
  - **Link(s)** — arXiv / DOI, in `--cyan`.
- Newest first.

### 5.4 Preprints
- Same structure as Publications, separate `h2` "Preprints".

**Content should live in the HTML directly** (it's a small static site). Structure
each publication so it's trivial for a non-coder to copy an existing block and edit
the text. Add an HTML comment above the list showing the template for one entry.

---

## 6. Layout & visual details

- Comfortable vertical rhythm: ~2.5rem between sections, ~1rem between publication
  entries.
- Section headings can have a subtle bottom hairline (`border-bottom: 1px solid
  var(--border)`) for structure — optional, keep it light.
- Links: no button styling, just colored text with underline-on-hover. Smooth
  `transition: color 0.15s`.
- Selection highlight: style `::selection` with `background: var(--border); color:
  var(--fg)`.
- Body padding: `2.5rem 1.25rem` on mobile, more breathing room on desktop.
- No box shadows, no gradients — flat surfaces only. It should feel like a clean
  terminal/editor, matching the eldritch origin.

---

## 7. Responsive behavior

- Mobile-first CSS. Single breakpoint around **720px** is enough.
- Content column: `width: min(720px, 100%)`, `margin: 0 auto`.
- Ensure tap targets (links) have adequate spacing on mobile.
- Header image scales to container width, `height: auto`.
- Test at 320px, 768px, 1200px.

---

## 8. Accessibility

- Color contrast AA minimum (palette above is designed for this).
- Real semantic headings in order (one `h1`, then `h2`s).
- All links have descriptive text (no "click here" for the CV — use "My CV").
- `<img>` header image has meaningful `alt`.
- Focus states visible: `a:focus-visible { outline: 2px solid var(--green);
  outline-offset: 2px; }`.
- `<html lang="en">`, proper `<title>` and `<meta name="description">`.
- Respect `prefers-reduced-motion` if any transitions are added.

---

## 9. Optional enhancements (implement only if requested)

- **Light/dark toggle:** The eldritch theme is inherently dark; a light variant is
  out of scope unless asked. If added, use a `data-theme` attribute + a small
  vanilla-JS toggle, persisted in `localStorage`. Keep dark as default.
- **Smooth scroll** for any in-page anchor nav.
- **Print stylesheet** so the page prints cleanly on white (useful for committees).
- A tiny top nav linking to sections — only if the page grows long.

---

## 10. Hosting on GitHub Pages

Deliver a repo ready to publish. Two common setups — implement the **user-site**
approach unless told otherwise:

**Option A — user/organization site (recommended, cleanest URL):**
1. Repo must be named exactly `<username>.github.io`.
2. `index.html` at repo root.
3. Push to the `main` branch.
4. In repo **Settings → Pages**, set Source = "Deploy from a branch", Branch =
   `main`, folder = `/ (root)`.
5. Site goes live at `https://<username>.github.io/` within a minute or two.

**Option B — project site (any repo name):**
1. Same as above but the URL becomes `https://<username>.github.io/<repo-name>/`.
2. Because of the subpath, **all asset paths must be relative** (already required
   in §2).

**Also include:**
- A `README.md` with: what the site is, how to run locally
  (`python3 -m http.server` from the repo root, then open `localhost:8000`), and
  how to edit content (point to the publication-entry template comment).
- A `.gitignore` (OS/editor junk: `.DS_Store`, `Thumbs.db`, `.vscode/`).
- A `favicon.svg` or `favicon.ico` — a simple eldritch-green glyph on the dark
  background is fine.
- A `CNAME` file **only if** the user provides a custom domain (leave out
  otherwise).

---

## 11. Deliverable file structure

```
<username>.github.io/
├── index.html
├── styles.css
├── favicon.svg
├── README.md
├── .gitignore
└── files/
    ├── cv.pdf          (placeholder — user replaces)
    └── header.png      (placeholder header/fractal image — optional)
```

---

## 12. Content placeholders to leave for the user

Wherever real content isn't known, insert clearly-marked placeholders the user can
find-and-replace:

- `Your Name`
- `Ph.D. Candidate in [Field]`
- `you [at] university [dot] edu`
- `[Office / building / room]`
- Institution/advisor links
- About-me prose (2 short paragraphs of lorem-style placeholder, clearly marked)
- 2–3 example publication entries following the template
- 1–2 example preprint entries

Mark every placeholder with an HTML comment like
`<!-- REPLACE: your name -->` so they're easy to locate.

---

## 13. Acceptance checklist

- [ ] Single page, loads with zero JS errors and no external JS deps.
- [ ] Eldritch palette applied via CSS variables; accents used per §3.
- [ ] Times New Roman applied via `--font-body`; no web fonts loaded.
- [ ] All four content areas present: identity, About, Publications, Preprints.
- [ ] Publication entry template documented in an HTML comment.
- [ ] Fully responsive at 320 / 768 / 1200px; content column capped ~720px.
- [ ] Relative asset paths throughout.
- [ ] Passes AA contrast; keyboard-focusable links with visible focus.
- [ ] `README.md`, `.gitignore`, favicon, and `files/` placeholders included.
- [ ] Ready to publish via GitHub Pages with the steps in §10.
