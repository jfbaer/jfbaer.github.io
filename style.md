---
# =====================================================================
#  style.md — the design system, in one file.
#
#  Every `key: value` line below becomes a CSS custom property that
#  build.py writes into styles.css. This is where you reskin the site.
#
#  Rules the build follows:
#    • A key ending in `-light` / `-dark` is a THEME PAIR. The build
#      emits both, uses the -light value by default, and swaps to the
#      -dark value under the dark-mode toggle. Palette colours are pairs.
#    • Any other key is a single value used in both themes (fonts,
#      spacing, widths, type sizes).
#    • `key: value`  ->  `--key: value` in styles.css. So `accent-light`
#      drives `--accent`, `measure` drives `--measure`, etc.
#    • Lines starting with `#`, and any prose outside `key: value`, are
#      ignored — comment freely.
#
#  Modelled on Kyle Ormsby's e-infinity.space design system: a warm
#  paper/ink palette declared once as light/dark pairs, one serif for
#  everything + one mono for labels, a single spacing scale, two widths.
#  Change these values to make it yours.
# =====================================================================


# ------------------------------------------------------------------ #
#  1. PALETTE  (light / dark pairs)
#
#  Seven roles, no eighth. Restraint does most of the work — resist
#  adding more colours. Retheme by editing these fourteen values.
#
#  Light  = Catppuccin Latte (AMS variant): black ink on white paper,
#           grayscale neutrals, a Latte blue accent.
#  Dark   = Nord: polar-night paper, snow-storm ink, a frost accent.
#  (themes/catppuccin-latte-ams.tex and themes/nord.tex are the sources.)
# ------------------------------------------------------------------ #

# page background            Latte Base / Nord Base (nord0)
paper-light:       #FFFFFF
paper-dark:        #2E3440

# sunk surfaces: code blocks, the header well, block quotes
# Latte Crust / Nord Surface0 (nord1, an elevated well on the dark base)
paper-sunk-light:  #EBEBEB
paper-sunk-dark:   #3B4252

# primary text               Latte Text / Nord Text (nord6)
ink-light:         #000000
ink-dark:          #ECEFF4

# secondary text: labels, dates, meta, contact, footer
# Latte Subtext0 / Nord Overlay2
muted-light:       #5A5A5A
muted-dark:        #7B88A1

# hairlines, dividers, the trailing rule after a section label
# Latte Surface0 / Nord Surface1 (nord2)
rule-light:        #DCDCDC
rule-dark:         #434C5E

# the one accent: links, link hover, focus rings, your name
# Latte Blue / Nord Frost (nord8) — a blue on both, so the toggle keeps hue
accent-light:      #1E66F5
accent-dark:       #88C0D0

# faint accent wash: link-hover background, callouts (a tint of the accent)
accent-bg-light:   #E0E9FD
accent-bg-dark:    #3A4A54


# ------------------------------------------------------------------ #
#  2. TYPE
#
#  Two faces with strictly divided jobs. Newsreader (serif) for ALL
#  body copy and ALL headings — headings scale by size and tracking,
#  never by weight (nothing here is bold). IBM Plex Mono only as the
#  .label workhorse: nav, dates, tags, section markers, footer, toggle.
#  Both are self-hosted in fonts/ (see fonts/fonts.css).
# ------------------------------------------------------------------ #

font-serif:  'Literata', Georgia, 'Times New Roman', serif
font-mono:   'Roboto Mono', ui-monospace, Menlo, monospace

# fluid body size, line height, and the negative tracking on headings
body-size:        clamp(0.95rem, 0.90rem + 0.22vw, 1.00rem)
line-height:      1.62
heading-tracking: -0.015em
heading-weight:   400

# the .label look: lowercase + tracked mono (not uppercase + tracked)
label-size:       0.7rem
label-weight:     500
label-tracking:   0.08em
label-transform:  lowercase


# ------------------------------------------------------------------ #
#  3. LINKS
#
#  No text-decoration anywhere. Links are a 1px accent gradient under-
#  line that thickens to 2px on hover, sitting just above the baseline
#  so descenders clear it.
# ------------------------------------------------------------------ #

link-underline-size:    1px
link-underline-hover:   2px
link-underline-offset:  0.08em


# ------------------------------------------------------------------ #
#  4. SPACING SCALE  (one scale, used everywhere)
# ------------------------------------------------------------------ #

s1: 0.25rem
s2: 0.5rem
s3: 0.75rem
s4: 1rem
s5: 1.5rem
s6: 2rem
s7: 3rem
s8: 4.5rem
s9: 7rem


# ------------------------------------------------------------------ #
#  5. WIDTHS  (two layout primitives)
#
#  .prose columns at --measure; .wrap breaks out to --wide for galleries
#  or wide tables. The page gutter is 2.5rem, baked into base.css.
# ------------------------------------------------------------------ #

measure: 92ch
wide:    74rem
---

# style.md

This file has no visible content of its own — it is read entirely from
the frontmatter above by `build.py`, which turns each `key: value` into a
CSS custom property in `styles.css`. Edit the values above and run
`python3 build.py` (or `python3 serve.py` for live reload).
