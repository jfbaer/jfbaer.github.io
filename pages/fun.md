---
title: Steenrod art
description: A library of indecomposable modules over the 2-primary Steenrod algebra; those rigorously certified realizable as the cohomology of a spectrum are marked.
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

A module $M$ is **realizable** if it is the cohomology of a spectrum — some $X$
with $H^{*}(X;\mathbb{F}_2) \cong M$ as $\mathcal{A}$-modules. The obstructions to
building such an $X$ lie in the self-Ext groups
$\mathrm{Ext}_{\mathcal{A}}^{\,s,\,s-2}(M,M)$ for **all** $s \ge 3$ (Toda's
realization theorem, via Goerss–Hopkins obstruction theory); if they all vanish,
$M$ is realizable.

Modules marked **✓** are **rigorously certified** by this test: $M$ is free over
$\mathcal{A}(0)$ — its $\mathrm{Sq}^1$-Margolis homology vanishes, ruling out the
infinite $h_0$-towers that would otherwise keep the obstruction groups from ever
vanishing — and its stem-$(-2)$ groups vanish up through the Adams vanishing line,
computed from a minimal free resolution of $M$. The criterion is *sufficient, not
necessary*: an unmarked module is **not** disproven — many are realizable but not
certifiable this way (even $C\eta$ and the sphere's $\mathbb{F}_2 = H^{*}(S^0)$ are
realizable yet uncertified). We make no claims about uniqueness of realizations.

Click a module to copy its sseq-format JSON.

<!-- include: steenrod-gallery.partial.html -->
