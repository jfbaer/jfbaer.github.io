# viz/adams-charts/

The interactive **unstable Adams charts** launched by the button on the
research page (`pages/research.md` → `research.html`).

The button links to `viz/adams-charts/index.html` and opens it in a new tab.
Right now that `index.html` is a **placeholder** ("coming soon"). Nothing else
in the build references the individual charts, so swapping in the finished set
is a drop-in.

## Slotting in the finished charts

The generator (in `~/lambda-ehp/charts/interactive_charts/`) produces a
self-contained bundle: an `index.html` navigator plus one
`S<stem>_E<page>.html` file and matching `S<stem>_E<page>.json` per chart.

1. Delete the placeholder `index.html` in this folder.
2. Copy the whole generated bundle in here, e.g.:

   ```sh
   cp ~/lambda-ehp/charts/interactive_charts/* viz/adams-charts/
   ```

   The generated `index.html` becomes the new landing page — the button
   already targets it, so no edit to `research.md` is needed.
3. `python3 build.py` (or just reload under `serve.py`). The charts are static
   assets served as-is; the Python build never touches this folder.

That's it — the button goes live the moment the real `index.html` is in place.

## Heads-up: third-party (CDN) requests

The current generated charts pull KaTeX, `svg-pan-zoom`, `hammer.js`,
`path-data-polyfill`, and a Computer Modern web font from `cdn.jsdelivr.net`.
That breaks the site's "zero third-party requests" property (see `viz/README.md`
and `README.md`): every visitor's browser would hit jsDelivr, and the charts
won't render offline. When you're ready, we can vendor those libraries locally
(drop them in `vendor/` and rewrite the `<script>`/`<link>` tags to relative
paths) so the charts stay self-hosted like the rest of the site.
