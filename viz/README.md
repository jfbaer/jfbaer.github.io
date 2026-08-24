# viz/

Self-contained interactive work — the HTML/JS/WebGL animations you
generate from your mathematics. One folder or one `.html` file per piece,
each fully standalone (inline its own CSS/JS, or keep assets alongside it).

Embed a piece from `content.md` (or any `pages/*.md`) with an iframe — raw
HTML passes through the build untouched:

```html
<iframe class="viz" src="viz/adams-chart/index.html"
        title="Interactive Adams chart" loading="lazy"></iframe>
```

Add the `bleed` modifier to break out wider than the prose column:

```html
<iframe class="viz bleed" src="viz/homotopy-flow.html"
        title="Homotopy flow" loading="lazy"></iframe>
```

Keeping each animation self-contained (no CDN scripts — vendor three.js or
whatever you use locally) preserves the site's "zero third-party requests"
property: no external host ever sees your visitors.
