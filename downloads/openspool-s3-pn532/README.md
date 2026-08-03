# OpenSpool carrier: ESP32-S3 terminal adapter + PN532 V3

This folder contains a **first-fit, parametric bench carrier** for the hardware
used in the ParaMat polymer-filament OpenSpool demonstrator:

- AITRIP/YD-style ESP32-S3-WROOM-1 N16R8, dual USB-C, 44-pin controller;
- ESP32-S3-TA-44P-style green screw-terminal adapter (`80 × 70 mm` nominal);
- red Elechouse-style PN532 NFC Module V3 (`42.7 × 40.4 × 4 mm` nominal).

The controller plugs into the terminal adapter; the carrier mounts the adapter,
not the ESP32 header edges. The open layout is intended to leave the screw
terminals, USB-C ports, and BOOT/RST buttons accessible. The PN532 sits beside it
with its antenna face open and an intentional 15 mm in-plane board gap.

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
- orientation: flat base on the build plate;
- layer height: 0.20 mm;
- walls: 4;
- top/bottom layers: 5;
- infill: 20% or higher;
- supports: none;
- brim: normally unnecessary; add a brim or mouse ears if corners lift.

Suggested order:

1. Measure the actual adapter-hole pattern.
2. Print the two small coupons.
3. Confirm the PN532 clip and M2.5 screw fit.
4. Print the full carrier.
5. Remove any elephant-foot flare before inserting electronics.

## Assembly

1. Power off and disconnect the electronics.
2. Place the green terminal adapter over the four bosses. Install four
   M2.5 × 6 mm screws through its mounting holes and tighten only until seated.
3. Plug the YD/AITRIP ESP32-S3 into the adapter with its USB-C ports facing the
   open outside end.
4. Place the PN532 antenna face up in the smaller bay. Its eight-pin auxiliary
   header row must remain unpopulated where a clip crosses it. Put the four-pin
   I2C edge toward the center opening and flex the clips only enough to seat it.
5. Route GND/VCC/SDA/SCL through the center. Do not place a tie, wire bundle, or
   metal hardware across the antenna loop.
6. Connect both USB-C cables and all intended wires before judging access.

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
- tag read and write work with ESP32 off, powered, and Wi-Fi active;
- range remains reliable beside the printer and on the final mounting surface.

Only after those checks should the model be described as physically validated.

## Dimensional sources and license boundary

- [ESP32-S3-TA-44P distributor specification](https://www.hestore.eu/en/prod_10048181.html):
  reference `70 × 80 × 12 mm`, `32 × 72.5 mm` pattern, `Ø3 mm` holes;
- [YD-ESP32-S3 board reference](https://github.com/profharris/YD-ESP32-S3_ESP32-S3-WROOM-1_Dev):
  44 pins, dual USB-C, approximately `1.1 × 2.5 in`;
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
