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
