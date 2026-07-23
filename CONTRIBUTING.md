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

No GitHub account? Email the same information (label photo, values, source) to
**paramat3d@sunn3d.com** — we'll enter it with you credited as the source.

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

## Most-wanted experiments (ranked by variance destroyed)

Our published uncertainty budget says the prediction interval is dominated by what studies
*don't report*. If you're planning a reviewed DoE (or a careful home experiment with stated
methods), these are the gaps — each one directly narrows the public predictor's error bars:

1. **Dry-vs-wet printed coupons** — one PLA + one PA, dried / week-ambient / saturated,
   ≥3 replicates (~12 coupons). Filament water state is the single biggest unreported term
   (~14% of strength). Neat-filament sensitivity is measured; *printed-part* deltas are not.
2. **Part-cooling fan sweep** — one hot-bonding family (ABS/ASA/PC), fan 0/50/100%,
   everything else fixed, ≥3 reps (~9 coupons). Today's fan term comes from a single study
   where fan, nozzle and bed temperature moved together — it urgently needs independent
   replication. Cheapest high-value experiment on this list.
3. **Solo-vs-batch plate layout** — the same coupon printed alone, ×4, and ×9 per plate,
   3 reps (~9 coupons). Interlayer time / thermal history, ~10%; essentially unpublished.
4. **Z-orientation series beyond PLA/ABS** — upright coupons, ≥3 reps (PETG, ASA, PC, PA…).
   Z retention is the most safety-relevant number and our data covers two families.
5. **Specimen geometry cross-test** — one material across ISO 527-1B vs ASTM D638-I and two
   thicknesses (~12 coupons). Standards disagree by 13–20% on the same material.
6. **Infill pattern at stated density** — gyroid vs grid vs rectilinear *with the density
   printed in the paper*. No open study states both; until one does, pattern stays unmodeled.

**Golden fields** (report these and your data enters the model at replicate-floor accuracy):
infill % *and* pattern · wall count · flow/extrusion multiplier · measured part density ·
filament moisture/drying state · fan % · nozzle & bed temps (set *and* measured if you can) ·
print speed · specimen standard & orientation · printer model · n per condition with SD.
