# Contributing corrections & missing filaments

Found a wrong value, or a filament we don't list? **Add or fix a row in
[`curated.csv`](curated.csv) and open a pull request** — the edit button on that file
does the fork + PR for you. Reviewed entries are merged into the dataset on the next
rebuild.

## Rules (what makes a PR mergeable)

1. **One row per product line** (brand + product, e.g. `YOYI,PETG`). Colors/sizes of the
   same product are one row.
2. **Provenance is required.** Say exactly where each value comes from — the spool label
   text, or a manufacturer spec-page URL. *"Works for me"* tuning values belong in an
   issue, not in curated.csv (the dataset records what sources state, not anecdotes).
3. **Only fill what your source states.** Leave unknown fields empty — don't guess.
   Temperatures are °C; `nozzle_min_c`/`nozzle_max_c` is the printed range (a single
   stated temperature goes in both).
4. No values copied from other databases or from AGPL slicer profiles — labels and
   manufacturer pages only.

Prefer not to edit CSV? [Open an issue](../../issues/new) with a photo of the label and
we'll take it from there.

Data license: contributions are accepted under CC BY 4.0.

## Certified test results (mechanical / property data)

Measured properties (tensile, modulus, roughness, HDT, …) are the most valuable data we can
get — and the rules are stricter than for print settings:

1. **Publish openly first, ideally.** Our policy is to *source from open databases, not silo
   data*. If you can, deposit your results where anyone can use them — Zenodo/OSF (gets a DOI),
   a university repository, or an Open3DPP-schema dataset — then open an issue pointing us at
   it. We ingest from there, with your work cited.
2. **Or PR a row into [`outcomes.csv`](outcomes.csv)** when a public deposit isn't practical.
   One row per (material × test condition × property).
3. **Every row needs its method.** Test standard (e.g. ISO 527-2/1A, ASTM D638 Type I,
   ISO 4287 Ra), specimen orientation (XY / Z / 45°), full process settings (temps, speed,
   layer height, infill, raster angle), printer model, number of specimens, and a link to the
   report or dataset. "Certified" means a traceable method — results without a standard and
   settings can't be merged.
4. Anecdotal single prints belong in an issue, not the dataset.

Accepted results feed the public consensus database (CC BY 4.0, you're credited via the source
link) and the property-prediction validation set.
