---
title: Steenrod art
description: A library of finitely generated modules over the 2-primary Steenrod algebra, realizable as the cohomology of finite cell complexes.
---

<style>
  /* legend colours for the Sq words below — same theme-aware palette the
     module diagrams use (Catppuccin Latte in light, Nord in dark). */
  .sq1  { color:#1e66f5; } .sq2  { color:#8839ef; } .sq4 { color:#fe640b; }
  .sq8  { color:#40a02b; } .sq16 { color:#04a5e5; }
  [data-theme='dark'] .sq1  { color:#81a1c1; }
  [data-theme='dark'] .sq2  { color:#b48ead; }
  [data-theme='dark'] .sq4  { color:#d08770; }
  [data-theme='dark'] .sq8  { color:#a3be8c; }
  [data-theme='dark'] .sq16 { color:#88c0d0; }
</style>

This page is a library of finitely generated modules over the mod-2 Steenrod
algebra $\mathcal{A}$, each with a single generator in internal degree 0. Nodes
are the generators, placed vertically by internal degree; a line between two
nodes denotes the action of $\mathrm{Sq}^{2^n}$, with $n$ shown by both the
line's length and its color — $\mathrm{Sq}^1$, $\mathrm{Sq}^2$, $\mathrm{Sq}^4$,
$\mathrm{Sq}^8$, and $\mathrm{Sq}^{16}$ are <span class="sq1">blue</span>,
<span class="sq2">purple</span>, <span class="sq4">orange</span>,
<span class="sq8">green</span>, and <span class="sq16">light blue</span>.

Each module is indecomposable, and no two are isomorphic.

Every module shown is also realizable. A module $M$ over $\mathcal{A}$ is listed
as realizable when the obstruction groups $\mathrm{Ext}_{\mathcal{A}}^{s,\,s-2}(M,M)$,
for $3 \le s \le \operatorname{diam}(M)+2$, all vanish — the stem-$(-2)$
obstructions, computed from a minimal free resolution of $M$, to realizing $M$
as the cohomology $H^{*}(X;\mathbb{F}_2)$ of a spectrum $X$. We make no claims
about the uniqueness of these realizations.

Click a module to copy its sseq-format JSON.

<!-- include: steenrod-gallery.partial.html -->
