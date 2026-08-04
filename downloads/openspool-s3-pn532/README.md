# OpenSpool carrier + snap cover: ESP32-S3 terminal adapter + PN532 V3

This folder contains a **first-fit, parametric bench carrier** for the hardware
used in the ParaMat polymer-filament OpenSpool demonstrator:

- AITRIP/YD-style ESP32-S3-WROOM-1 N16R8, dual USB-C, 44-pin controller;
- ESP32-S3-TA-44P-style green screw-terminal adapter (`80 × 70 mm` nominal);
- red Elechouse-style PN532 NFC Module V3 (`42.7 × 40.4 × 4 mm` nominal).

The controller plugs into the terminal adapter; the carrier mounts the adapter,
not the ESP32 header edges. A separate low-profile inverted tray snaps around
the outside of the existing carrier. Four compliant side tongues and local
upper stops form a segmented edge groove, so no additional cover screws are
needed. Both long cover walls are closed. The short +X end wall is also closed
except for two compact, bounded USB-C apertures; no general-purpose wire exits
are provided. The PN532 remains beside the adapter with an intentional 15 mm
in-plane board gap.

This is not a production-validated enclosure. Published dimensions created the
first model; the physical print and real boards must confirm mounting-hole
spacing, fit, cable access, clip behavior, and NFC range.

## Measure before the full print

The current CAD uses a `72.5 × 32 mm` hole-center pattern and `Ø3 mm` holes from
a published reference adapter. Superficially similar AITRIP/reseller boards can
differ. Measure the actual green board center-to-center in both directions and
measure the hole diameter before printing the full carrier. Update
`ADAPTER_HOLE_PITCH_X` and `ADAPTER_HOLE_PITCH_Y` if required.

## Files

- `exports/openspool_s3_pn532_snap_cover.stl` - roof-down, support-free cover;
- `exports/openspool_s3_pn532_snap_cover.step` - assembled-orientation cover;
- `exports/snap_cover_latch_fit_coupon.stl` - one real latch segment to
  test against the printed carrier before committing to the full cover;
- `exports/openspool_s3_pn532_snap_cover_preview.png` - cover preview;

- `exports/openspool_s3_pn532_carrier.stl` — generated first-fit carrier;
- `exports/openspool_s3_pn532_carrier.step` — editable solid for Rhino/CAD;
- `exports/openspool_s3_pn532_fit_check.step` — carrier plus simplified envelopes;
- `exports/pn532_clip_fit_coupon.stl` — print first to test the PN532 snap fit;
- `exports/m2p5_screw_fit_coupon.stl` — three pilot-slot widths for the screws;
- `exports/openspool_s3_pn532_carrier_preview.png` — site/social preview;
- `openspool_s3_pn532_mount.py` — CadQuery source and fit parameters;
- `test_mount.py` — deterministic geometry, plate-envelope, and spacing checks;
- `LICENSE-Hardware.txt` — CERN-OHL-S-2.0 scope and source-location notice.

The current nominal footprint is `145.7 × 78.0 × 10.8 mm`, which is within the
Bambu A1 mini's `180 × 180 mm` build-plate envelope. Actual slicer placement,
adhesion, and printer calibration still apply.

The cover's outside envelope is `149.6 x 81.9 x 27.6 mm`; its assembled
top is `26.6 mm` above the carrier datum. Its footprint is also within
the Bambu A1 mini's `180 x 180 mm` build-plate envelope.

## Snap-cover controls and clearances

The cover has `0.35 mm` nominal XY clearance per carrier side, `1.6 mm`
walls, and a `1.6 mm` roof. Four side latches catch below the carrier
while four local stops sit above its `2.8 mm` edge. The fit is
intentionally light-duty and parametric; print
`snap_cover_latch_fit_coupon.stl` and try it on the real carrier first.
Increase `COVER_XY_CLEARANCE` or reduce `COVER_LATCH_HOOK_DEPTH` if
the coupon produces whitening or requires excessive force.

The +X end has two nominal `12 x 9 mm` USB-C apertures centered at
`Y = -7 mm` and `Y = +7 mm`, with vertical center `Z = 20.5 mm`.
That leaves a `2 mm` center rib and the lower end wall intact. The openings
run nominally from `Z = 16 mm` to the `25 mm` roof underside. These
centers are first-fit estimates relative to the provisional controller/adapter
origin, not manufacturer connector-placement CAD. Confirm both USB-C plug
alignments on the physical assembly.

Two `4.2 mm` tool holes provide top access to RST and BOOT. Their
longitudinal centers are derived from the board's `2.54 mm` header grid:
RST is midway between pins 38/39 (`-5.08 mm` from controller center) and
BOOT is midway between pins 36/37 (`0.00 mm`). RGB is aligned midway
between pins 9/10 on the opposite row (`+10.16 mm`). The current
transverse estimates are `+5.05 mm` for both buttons and `-5.05 mm`
for RGB.

RGB is not a through-hole. An internal `7 mm` light well leaves a
`0.45 mm` exterior membrane so an unfilled white cover can diffuse the
onboard status LED. The pin-grid relationships are known, but the
adapter-to-controller origin and transverse offsets remain first-fit estimates
from the supplied image, not manufacturer placement CAD. Confirm them on the
physical assembly before treating the openings as validated.

## Fasteners

Use **four M2.5 × 6 mm pan-head screws**, optionally with M2.5 washers. Do not
substitute M3: M3 is nominally the same diameter as the reference PCB hole and
may bind on board or plating tolerances.

No nuts or threaded inserts are required. Each screw forms a light-duty thread
in a short blind slot in the printed boss. This is appropriate for a stationary
bench carrier; it is not designed for vibration or transport.

Print `m2p5_screw_fit_coupon.stl` first. With the coupon in the orientation
exported by the source, the pilots are `1.9`, `2.1`, and `2.3 mm` from negative
X to positive X. Start with `2.1 mm`. Select the width that accepts the screw
firmly without splitting the boss, update `SELF_TAP_SLOT_WIDTH` if needed, and
regenerate. Tighten only until the PCB is seated. Do not torque or repeatedly
remove the screw.

## Printing

- material: PETG preferred; PLA is acceptable for a dimensional test;
- carrier orientation: flat base on the build plate;
- cover orientation: use the exported STL as supplied, exterior roof face down;
- layer height: 0.20 mm;
- walls: 4;
- top/bottom layers: 5;
- infill: 20% or higher;
- supports: none;
- brim: normally unnecessary; add a brim or mouse ears if corners lift.

Use plain, unfilled white PETG or PLA for the first cover. Carbon-fiber,
metal-filled, or conductive filament can reduce NFC performance and will not
provide the intended RGB diffusion. Each bounded USB-C aperture creates an
approximately 12 mm bridge in the roof-down orientation. That is normally a
small bridge for a tuned FDM printer, but inspect the slicer preview and enable
the printer/material bridge settings or a minimal local support if needed.

Suggested order:

1. Measure the actual adapter-hole pattern.
2. Print the three small coupons, including the cover-latch segment.
3. Confirm the PN532 clip and M2.5 screw fit.
4. Print the full carrier, then the roof-down cover.
5. Remove any elephant-foot flare before inserting electronics.

## Assembly

1. Power off and disconnect the electronics.
2. Place the green terminal adapter over the four bosses. Install four
   M2.5 × 6 mm screws through its mounting holes and tighten only until seated.
3. Plug the YD/AITRIP ESP32-S3 into the adapter with its USB-C ports facing the
   +X cover end and its two bounded apertures.
4. Place the PN532 antenna face up in the smaller bay. Its eight-pin auxiliary
   header row must remain unpopulated where a clip crosses it. Put the four-pin
   I2C edge toward the center opening and flex the clips only enough to seat it.
5. Route GND/VCC/SDA/SCL through the center. Do not place a tie, wire bundle, or
   metal hardware across the antenna loop.
6. Complete the intended internal wiring and power the assembly off. The cover
   intentionally provides no side wire exits; confirm no wire crosses its
   perimeter or latch path. Disconnect USB-C cables before fitting the cover.
7. Align the cover over the carrier, engage one long edge, then press the
   opposite long edge only until the four latches click below the plate.
8. Insert the intended USB-C plug or plugs through the two bounded end
   apertures. Do not force a misaligned connector or oversized overmold.
9. Use a small nonmetal probe through the two top holes to verify RST and BOOT.
   Confirm the RGB indication is visible through the thin membrane.

Elechouse directs wires crossing antenna traces to cross at roughly 90°. The
PN532 PCB bottom sits about 8.3 mm above the mounting surface. If the carrier is
placed on the A1 mini's metal structure, compare read/write range on a nonmetal
table and in the intended location before relying on it.

## Regenerate and test

```powershell
cd path\to\openspool_s3_pn532_mount
py -3.11 openspool_s3_pn532_mount.py
py -3.11 -m unittest -v test_mount.py
py -3.11 package_public_release.py
py -3.11 package_public_release.py --check
```

CadQuery `2.7.0` and CairoSVG were used for the current exports. Rhino can open
the STEP files directly.

## Fit/RF acceptance checklist

- measured adapter pattern matches the CAD inputs;
- adapter drops over all four bosses without bending the PCB;
- all four screws start straight and seat without splitting a boss;
- PN532 inserts without white stress marks or excessive clip force;
- both USB-C plugs fit simultaneously;
- every used screw terminal and BOOT/RST remain reachable;
- cover snaps on without cracks, stress whitening, or PCB contact;
- both bounded USB-C apertures align without loading either board connector;
- the 2 mm USB center rib and lower end wall remain intact after printing;
- closed long walls and latch slots do not trap or abrade internal wires;
- RST/BOOT respond through the tool holes and RGB is visible through the membrane;
- tag read and write work with ESP32 off, powered, and Wi-Fi active;
- range remains reliable beside the printer and on the final mounting surface.

Only after those checks should the model be described as physically validated.

## Dimensional sources and license boundary

- [ESP32-S3-TA-44P distributor specification](https://www.hestore.eu/en/prod_10048181.html):
  reference `70 × 80 × 12 mm`, `32 × 72.5 mm` pattern, `Ø3 mm` holes;
- [YD-ESP32-S3 board reference](https://github.com/profharris/YD-ESP32-S3_ESP32-S3-WROOM-1_Dev):
  44 pins, dual USB-C, approximately `1.1 × 2.5 in`;
- [RI SHENG ST-1185S switch](https://www.lcsc.com/product-detail/C589191.html):
  nominal 4 x 3 x 2 mm component envelope identified by the YD schematic;
- [XINGLIGHT XL-5050RGBC-WS2812B](https://datasheet.lcsc.com/lcsc/2209191001_XINGLIGHT-XL-5050RGBC-WS2812B_C2843785.pdf):
  nominal 5 x 5 x 1.6 mm onboard RGB package identified by the YD schematic;
- [Elechouse PN532 V3 manual](https://www.elechouse.com/elechouse/images/product/PN532_module_V3/PN532_%20Manual_V3.pdf):
  `42.7 × 40.4 × 4 mm`, integrated antenna, and wiring guidance;
- [OpenSpool](https://github.com/spuder/OpenSpool): firmware and reference BOM.

The external OpenSpool Mini enclosure is not redistributed or remixed here. It
targets different controller hardware and carries its own terms. This carrier
is new parametric geometry based on published hardware envelopes.

The Covered Source and generated hardware artifacts are licensed under
`CERN-OHL-S-2.0`; see `LICENSE-Hardware.txt`. This license does not relicense
third-party boards, firmware, ParaMat datasets, prediction methods, or website
software. Files and resulting products are provided as-is and without warranty.
