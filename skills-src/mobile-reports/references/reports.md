# Reports and data pages

Adapted from MultiTool's former `html-report` skill; its design guidance derives
from Anthropic's Apache-2.0 frontend-design.

Use this mode for findings, comparisons, metrics, and analysis presented as
HTML. It shares the skill's export and browser checks. For a copied website or
course use snapshot mode instead: report structure must not change its content.

## Content and design

Design around the actual material and audience. A useful report can have a
title with period/scope, a short answer or summary, thematic sections with
evidence, and source/methodology notes. Include headline metrics only when the
data has meaningful ones; a narrative document needs no invented KPI band.
Choose tables, charts, and prose according to what makes the evidence legible.
Read `design.md` for a new design, preserving any supplied branding.

Every figure must trace back to the supplied or retrieved data. Keep units,
periods, denominators, locale formatting, and comparison bases explicit.
Preserve precision; distinguish estimates and illustrative data. Check that
totals and percentages reconcile and that prose matches the figures. Missing
values are missing values, not zero. Link actual sources where useful unless
the user requested no outgoing links.

Prefer readable lines, clear hierarchy, restrained emphasis, and responsive
tables. Right-align comparable numeric columns, put units in their headings,
and avoid making color the only way to read a result. A screenshot-shaped
report is not a replacement for selectable text and semantic markup.

## Charts

For small datasets, HTML tables, CSS bars, and inline SVG are portable. A
vendored/built library can also be embedded when interaction warrants it; a
CDN dependency cannot be part of an offline artifact. Avoid adding a chart
where a few values are clearer in a table.

- Bar/column lengths must be proportional, with a zero baseline unless a
  different baseline is explicitly explained. Show labels and units.
- Line charts need honest axes, periods, labels, and gaps for missing values.
- Pie/donut charts fit a few parts of one whole. Check the total and label
  the segments; many categories usually read better as bars or a table.
- SVG viewBox, coordinates, and stroke sizes must leave room for labels.
  Give graphics an accessible title/description and keep key values available
  as text, including when JavaScript is disabled for a primarily static report.

## Print and verify

Set the page language and title, semantic headings, useful captions, keyboard
focus for controls, and readable contrast. Reports should print without
clipped tables or missing content. A typical starting point is:

```css
@media print {
  body { background: white; color: black; }
  main { max-width: none; margin: 0; padding: 0; }
  nav, button, .screen-only { display: none; }
  table, figure { break-inside: avoid; }
  thead { display: table-header-group; }
}
```

Adapt that rule for long tables; keeping a table together must not make it
overflow the printed page. Expand report content hidden behind interactive
controls for print, and inspect the actual print rendering when possible.

Verify numbers, chart geometry, source attribution, mobile layout, and print
output. For an interactive dashboard also test its actual filters and state.
