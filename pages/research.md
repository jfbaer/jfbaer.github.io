---
title: Research
description: Research and preprints of Jake Francis Baer.
---

My favorite questions in mathematics involve geometrically flavored classification problems whose solutions depend on the explicit computation of some invariant of a space. I'm particularly interested in revisiting classical problems in homotopy theory and applying computer automation to methods traditionally done by hand.

<style>
  /* Two equal columns (bullets | chart) in a block that breaks out a little
     wider than the prose, so the pair reads compact and symmetric. */
  .focus-row{ position:relative; left:50%; transform:translateX(-50%);
              width:min(48rem, calc(100vw - 3rem));
              display:flex; gap:var(--s6); align-items:flex-start;
              justify-content:center; flex-wrap:wrap;
              margin-block:var(--s5) var(--s4); }
  /* share leftover space and WRAP long items, rather than widening the column
     until the chart is shoved out of the row. */
  .focus-row .focus-list{ flex:1 1 0; min-width:min(16rem, 100%); margin:0; }
  .focus-row .focus-list ul{ margin:0; }
  /* lead-in that introduces the bullets, kept in the column so it lines up
     with them (instead of sitting up in the full-width intro paragraph). */
  .focus-row .focus-lead{ margin:0 0 var(--s3); text-wrap:pretty; }
  .focus-row .focus-viz{ flex:0 0 auto; width:min(25rem, calc(100vw - 3rem)); }
  .focus-row .focus-viz figure{ margin:0; }
  /* aspect ratio matches the chart's own viewBox (420/312) so it fills the
     box with almost no letterboxing — bigger, bolder on the page. */
  .focus-row .focus-viz iframe{ display:block; width:100%;
              aspect-ratio:420 / 312; border:0; background:transparent; }
  .focus-row .focus-caption{ margin-top:var(--s3); text-align:center;
              text-transform:none; font-family:var(--font-mono);
              font-size:.64rem; line-height:1.5; letter-spacing:.02em;
              color:var(--muted); text-wrap:pretty; }
  /* the tall focus block already gives plenty of separation, so pull the
     first section heading up out of its default (large) top margin. */
  #homotopy-groups-of-spheres .rule-label{ margin-top:var(--s4); }
  @media (max-width:48rem){
    .focus-row{ left:0; transform:none; width:100%; }
  }
</style>
<div class="focus-row">
  <div class="focus-list">
    <p class="focus-lead">A few spectral sequences I've been thinking about recently:</p>
    <ul>
      <li>the unstable Adams and EHP sequence</li>
      <li>the Atiyah&ndash;Hirzebruch spectral sequence for real projective spectra</li>
      <li>the equivariant slice spectral sequence for higher real K-theories</li>
    </ul>
  </div>
  <div class="focus-viz">
    <figure>
      <iframe src="viz/spectral/chart.html" title="Interactive spectral sequence — click to turn the page forward, right-click to go back" loading="lazy" scrolling="no"></iframe>
      <figcaption class="focus-caption">a piece of the $C_4$-slice spectral sequence for $\mathrm{BP}^{(C_4)}\langle 1 \rangle$</figcaption>
    </figure>
  </div>
</div>

## Homotopy groups of spheres

One of my favorite problems in algebraic topology is the classification of homotopy types of finite cell complexes. The key ingredient in this classification problem is explicit knowledge of homotopy groups of spheres. 

<div class="cta">
  <a class="button" href="viz/adams-charts/index.html" target="_blank" rel="noopener">launch unstable adams charts</a>
</div>

This link will take you to the unstable Adams charts that I generated in a recent computer-based approach to computing some new homotopy groups of spheres. The $\mathrm{E}_2$-page was computed using the lambda algebra and Curtis algorithm. Unstable Adams differentials were deduced from stable Adams differentials using the algebraic EHP sequence and the unstable Leibniz rule. 

## Preprints/publications
<!-- entries -->

title: The algebraic Novikov spectral sequence for topological modular forms
authors: **Jake Francis Baer**
year: 2024
status: Submitted
arxiv: https://arxiv.org/abs/2404.05573

---

title: Stable comodule deformations and the synthetic Adams&ndash;Novikov spectral sequence
authors: **Jake Francis Baer**, Max Johnson, Peter Marek
year: 2024
status: Submitted
arxiv: https://arxiv.org/abs/2402.14274
