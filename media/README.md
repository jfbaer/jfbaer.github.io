# media/

Images used on the site: a photo of yourself, diagrams, spectral-sequence
charts, screenshots.

Reference them from `content.md` (or any `pages/*.md`):

```markdown
![A spectral sequence chart](media/ass-chart.png)
```

For a caption, use raw HTML (it passes through the build untouched):

```html
<figure>
  <img src="media/ass-chart.png" alt="Adams spectral sequence chart">
  <figcaption>The Adams spectral sequence for the sphere, s ≤ 20.</figcaption>
</figure>
```

For a headshot that floats beside your intro:

```html
<img class="portrait" src="media/me.jpg" alt="Jake Francis Baer">
```

Commit real image files here (PNG/JPG/SVG/WebP). Give them explicit
dimensions in the markup where you can, so the page doesn't reflow as they
load.
