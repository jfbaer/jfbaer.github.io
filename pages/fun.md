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

This page contains a library of finitely generated modules over the 2-primary
Steenrod algebra. Each module has a single generator in internal degree 0. The
generators are represented by nodes where the vertical position corresponds to
internal degree. Lines between nodes represent the action by $\mathrm{Sq}^{2^n}$.
The value of $n$ is denoted by the length of the line as well as by its color.
$\mathrm{Sq}^1$, $\mathrm{Sq}^2$, $\mathrm{Sq}^4$, $\mathrm{Sq}^8$, and
$\mathrm{Sq}^{16}$ are color coded by <span class="sq1">blue</span>,
<span class="sq2">purple</span>, <span class="sq4">orange</span>,
<span class="sq8">green</span>, and <span class="sq16">light blue</span>.

Each module is indecomposable and every module displayed lives in a distinct
isomorphism class.

Furthermore every module displayed here can be realized as the 2-primary
cohomology of a finite cell complex.

This is confirmed by computing the obstruction groups $\mathrm{Ext}(?)$ and
confirming that they are all zero. Therefore every module can be lifted to a
finite cell complex. We make no claims regarding the uniqueness of these lifts.

You can click on a module to copy the sseq-format JSON file for the module.

<!-- include: steenrod-gallery.partial.html -->
