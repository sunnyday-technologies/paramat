# Security reporting

ParaMat is a static, serverless tool published at <https://paramat3d.com/>. It
has no backend and no accounts, which removes most of the usual web attack
surface — but two things here reach beyond the browser tab, and those are where
the real risk sits:

1. **The data drives hardware settings.** The tool publishes nozzle and bed
   temperatures. A wrong or manipulated value is not a display bug — it can
   damage a printer or create a fire risk in a machine left running.
2. **It writes to physical tags.** The optional export writes OpenSpool NDEF
   records to NTAG215/216 tags over Web NFC.

Anything touching those two paths should be reported privately.

## Reporting

Preferred: GitHub's private reporting — **Security → Report a vulnerability** on
<https://github.com/sunnyday-technologies/paramat>.

If you cannot use GitHub, email **security@sunn3d.com**. Please do not open a
public issue for anything in the first three categories below.

## In scope

- Any path by which published print conditions can be altered — data poisoning
  in `data.json` or `curated.csv`, a build or deploy step that lets unreviewed
  values reach the live site, or a fault that makes the page display values
  other than what the dataset contains.
- Anything that makes the NFC write path emit a record other than the one the
  user confirmed, write without confirmation, or target an unintended tag.
- Script injection through material data, scanned barcode or QR content, OCR
  output, or an imported shelf file. QR handling is deliberately parse-only and
  must never navigate; a case where it does is in scope.
- Exposure of a user's local shelf data, or telemetry transmitting anything
  beyond the documented anonymous aggregate — telemetry is opt-in and off by
  default, so a fault that enables or widens it is a privacy defect.
- Personal data in the repository or dataset.

## Out of scope

- A vendor's published temperature being wrong at source. ParaMat reports
  third-party and consensus figures with provenance and verifies none of them;
  that is a data-quality issue — use the correction link or open an issue.
- Flammability or other properties not being shown when a label does not state
  them. That is intentional: they are reported "as stated" and never inferred.
- Browser or OS vulnerabilities in Web NFC, the camera, or the file picker.
  Report to the vendor; tell us if ParaMat's usage widens the impact.

## Response

We aim to acknowledge within five working days, and faster for anything that
could publish an unsafe temperature or affect the NFC write path. Corrections to
published values are reflected in the dataset with provenance intact.
