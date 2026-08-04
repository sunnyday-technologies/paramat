"""Parametric printable carrier for the ParaMat/OpenSpool bench hardware.

Target hardware:
* 80 x 70 mm ESP32-S3-TA-44P terminal adapter
* AITRIP/YD ESP32-S3-WROOM-1 N16R8 dual-USB-C, 44-pin board
* Elechouse-style red PN532 NFC Module V3 with integrated PCB antenna

The terminal adapter is the controller-side structure: four M2.5 screws pass
through its published 3 mm PCB holes into blind pilot slots in printed bosses.
The open carrier leaves every screw terminal, both USB-C ports, BOOT/RST, and
the PN532 reader face accessible. It is a first-fit prototype until physically
printed, assembled, and RF-tested.
"""

from __future__ import annotations

# SPDX-License-Identifier: CERN-OHL-S-2.0

from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import cairosvg


@dataclass(frozen=True)
class Board:
    length: float
    width: float
    thickness: float = 1.6


# Published nominal envelopes. The ESP32 envelope is used only in the STEP
# fit-check assembly because the 80 x 70 mm adapter retains the controller.
# The exact AITRIP/YD board in the demonstrator is 63 x 28 mm.
ESP32 = Board(length=63.00, width=28.00)
TERMINAL_ADAPTER = Board(length=80.00, width=70.00)
PN532 = Board(length=42.70, width=40.40)

CLEARANCE_PER_SIDE = 0.50
BASE_THICKNESS = 2.80
PN532_STANDOFF = 5.50
ADAPTER_STANDOFF = 6.00
ESP32_SOCKET_HEIGHT = 8.50
BOARD_GAP = 15.00
EDGE_MARGIN = 4.00
CORNER_RADIUS = 4.00

# PN532 snap geometry. TRUE_CLIP_OVERLAP is the actual horizontal overlap over
# the board, not the total lip width. A small coupon is exported for calibration.
CLIP_WALL = 1.20
CLIP_WIDTH = 5.50
TRUE_CLIP_OVERLAP = 0.40
CLIP_HEAD = 0.70

# ESP32-S3-TA-44P published pattern: 32 x 72.5 mm, 3 mm PCB holes.
# M2.5 is selected because M3 is nominally the same diameter as the PCB hole.
# The blind slot allows minor X-pattern error and lets a screw form a light-duty
# thread directly in PETG. Tune SLOT_WIDTH with a screw-fit coupon if needed.
ADAPTER_HOLE_PITCH_X = 72.50
ADAPTER_HOLE_PITCH_Y = 32.00
FASTENER_THREAD = "M2.5"
SELF_TAP_SLOT_LENGTH = 3.00
SELF_TAP_SLOT_WIDTH = 2.10
SELF_TAP_DEPTH = 5.00
MOUNT_BOSS_DIAMETER = 9.00

# Low-profile inverted cover. It snaps around the outside edge of the printed
# carrier; the local upper stop and lower hook form a segmented friction groove.
# Values remain first-fit parameters until the cover is printed on the intended
# machine and tried on the physical carrier.
COVER_XY_CLEARANCE = 0.35
COVER_WALL = 1.60
COVER_ROOF = 1.60
COVER_BOTTOM_Z = -1.00
COVER_ROOF_UNDERSIDE_Z = 25.00
COVER_TOP_Z = COVER_ROOF_UNDERSIDE_Z + COVER_ROOF
COVER_CORNER_RADIUS = CORNER_RADIUS + COVER_WALL

COVER_LATCH_WIDTH = 10.00
COVER_LATCH_SLOT = 0.80
COVER_LATCH_RELIEF_TOP_Z = 7.50
COVER_LATCH_HOOK_DEPTH = 0.70
COVER_LATCH_LEDGE_Z = -0.20
COVER_LATCH_STOP_BOTTOM_Z = 3.15
COVER_LATCH_STOP_HEIGHT = 0.70
COVER_LATCH_STOP_DEPTH = 0.65

USB_PORT_CENTER_Y = 7.00
USB_PORT_WIDTH = 12.00
USB_PORT_HEIGHT = 9.00
USB_PORT_CENTER_Z = 20.50
USB_PORT_ORIGIN_STATUS = "first_fit_unverified_controller_origin"

# Control locations are anchored to the controller's 2.54 mm pin grid. The
# longitudinal positions are high-confidence; the transverse offsets and the
# adapter-to-controller origin are first-fit and require physical confirmation.
RST_LOCAL_X = -5.08  # midpoint between pins 38 and 39
BOOT_LOCAL_X = 0.00  # midpoint between pins 36 and 37
RGB_LOCAL_X = 10.16  # midpoint between pins 9 and 10, opposite row
BUTTON_LOCAL_Y = 5.05
RGB_LOCAL_Y = -5.05
BUTTON_TOOL_HOLE_DIAMETER = 4.20
RGB_LIGHT_WELL_DIAMETER = 7.00
RGB_MEMBRANE_THICKNESS = 0.45


def rounded_box_xy(
    length: float,
    width: float,
    height: float,
    radius: float = CORNER_RADIUS,
) -> cq.Workplane:
    """Create a Z-positive box with rounded vertical edges."""

    return (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(radius, length / 4.0, width / 4.0))
    )


def pn532_supports(center_x: float) -> cq.Workplane:
    """Four nonmetal pads hold the PN532 above the mounting surface."""

    result = cq.Workplane("XY")
    inset_x = PN532.length / 2.0 - 5.0
    inset_y = PN532.width / 2.0 - 5.0
    for x_sign in (-1, 1):
        for y_sign in (-1, 1):
            pad = (
                cq.Workplane("XY")
                .center(center_x + x_sign * inset_x, y_sign * inset_y)
                .circle(3.0)
                .extrude(PN532_STANDOFF)
                .translate((0, 0, BASE_THICKNESS))
            )
            result = result.union(pad)
    return result


def pn532_side_clip(*, x: float, y_sign: int) -> cq.Workplane:
    """PETG-friendly clip with a true 0.4 mm overlap and insertion ramp."""

    board_edge = PN532.width / 2.0
    stem_inner = board_edge + CLEARANCE_PER_SIDE
    stem_outer = stem_inner + CLIP_WALL
    stem_center_y = y_sign * (stem_inner + CLIP_WALL / 2.0)
    stem_height = PN532_STANDOFF + PN532.thickness + 0.90
    stem = (
        cq.Workplane("XY")
        .center(x, stem_center_y)
        .box(CLIP_WIDTH, CLIP_WALL, stem_height, centered=(True, True, False))
        .translate((0, 0, BASE_THICKNESS))
    )

    inner = board_edge - TRUE_CLIP_OVERLAP
    outer = stem_outer
    lip_bottom = BASE_THICKNESS + PN532_STANDOFF + PN532.thickness + 0.25
    lip_top = lip_bottom + CLIP_HEAD
    if y_sign > 0:
        profile = [(inner, lip_bottom), (outer, lip_bottom), (outer, lip_top), (inner, lip_bottom + 0.10)]
    else:
        profile = [(-outer, lip_bottom), (-inner, lip_bottom), (-inner, lip_bottom + 0.10), (-outer, lip_top)]
    ramped_lip = (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(CLIP_WIDTH / 2.0, both=True)
        .translate((x, 0, 0))
    )
    return stem.union(ramped_lip)


def pn532_clips(center_x: float) -> cq.Workplane:
    """Four clips grip header-free PN532 edges without metal fasteners."""

    result = cq.Workplane("XY")
    clip_x = PN532.length / 2.0 - 8.0
    for x_sign in (-1, 1):
        for y_sign in (-1, 1):
            result = result.union(
                pn532_side_clip(x=center_x + x_sign * clip_x, y_sign=y_sign)
            )
    return result


def pn532_end_stops(center_x: float) -> cq.Workplane:
    """Split low stops prevent wire pull from sliding the PN532 out."""

    result = cq.Workplane("XY")
    stop_height = PN532_STANDOFF + 1.20
    stop_width = 5.0
    stop_x = PN532.length / 2.0 + CLEARANCE_PER_SIDE + CLIP_WALL / 2.0
    for x_sign in (-1, 1):
        for y_sign in (-1, 1):
            y = y_sign * (PN532.width / 2.0 - stop_width / 2.0)
            stop = (
                cq.Workplane("XY")
                .center(center_x + x_sign * stop_x, y)
                .box(CLIP_WALL, stop_width, stop_height, centered=(True, True, False))
                .translate((0, 0, BASE_THICKNESS))
            )
            result = result.union(stop)
    return result


def adapter_bosses(center_x: float) -> cq.Workplane:
    """Four bosses with blind M2.5 self-tapping adjustment slots."""

    result = cq.Workplane("XY")
    for x_sign in (-1, 1):
        for y_sign in (-1, 1):
            x = center_x + x_sign * ADAPTER_HOLE_PITCH_X / 2.0
            y = y_sign * ADAPTER_HOLE_PITCH_Y / 2.0
            boss = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(MOUNT_BOSS_DIAMETER / 2.0)
                .extrude(ADAPTER_STANDOFF)
                .translate((0, 0, BASE_THICKNESS))
            )
            pilot = (
                cq.Workplane("XY")
                .center(x, y)
                .slot2D(SELF_TAP_SLOT_LENGTH, SELF_TAP_SLOT_WIDTH)
                .extrude(SELF_TAP_DEPTH + 0.20)
                .translate((0, 0, BASE_THICKNESS + ADAPTER_STANDOFF - SELF_TAP_DEPTH))
            )
            result = result.union(boss.cut(pilot))
    return result


def cable_tie_slots(base: cq.Workplane, x: float) -> cq.Workplane:
    """Two optional tie slots in the non-RF center wiring channel."""

    slot = cq.Workplane("XY").slot2D(8.0, 2.8).extrude(BASE_THICKNESS + 1.0)
    for y in (-13.0, 13.0):
        base = base.cut(slot.translate((x, y, -0.5)))
    return base


def make_base() -> tuple[cq.Workplane, dict[str, float]]:
    """Build the one-piece printable carrier."""

    total_length = PN532.length + BOARD_GAP + TERMINAL_ADAPTER.length + 2.0 * EDGE_MARGIN
    total_width = max(
        TERMINAL_ADAPTER.width,
        PN532.width + 2.0 * (CLEARANCE_PER_SIDE + CLIP_WALL),
    ) + 2.0 * EDGE_MARGIN

    pn532_x = -total_length / 2.0 + EDGE_MARGIN + PN532.length / 2.0
    adapter_x = total_length / 2.0 - EDGE_MARGIN - TERMINAL_ADAPTER.length / 2.0
    channel_x = (
        pn532_x + PN532.length / 2.0 + adapter_x - TERMINAL_ADAPTER.length / 2.0
    ) / 2.0

    base = rounded_box_xy(total_length, total_width, BASE_THICKNESS)
    base = cable_tie_slots(base, channel_x)
    base = base.union(pn532_supports(pn532_x))
    base = base.union(pn532_clips(pn532_x))
    base = base.union(pn532_end_stops(pn532_x))
    base = base.union(adapter_bosses(adapter_x))

    metadata = {
        "total_length": total_length,
        "total_width": total_width,
        "total_height": BASE_THICKNESS + max(
            PN532_STANDOFF + PN532.thickness + 0.90,
            ADAPTER_STANDOFF,
        ),
        "pn532_center_x": pn532_x,
        "adapter_center_x": adapter_x,
        "channel_center_x": channel_x,
        "adapter_hole_pitch_x": ADAPTER_HOLE_PITCH_X,
        "adapter_hole_pitch_y": ADAPTER_HOLE_PITCH_Y,
    }
    return base.clean(), metadata


def controller_control_locations(metadata: dict[str, float]) -> dict[str, tuple[float, float]]:
    """Return first-fit top-control centers in carrier coordinates.

    X is derived from the controller's 2.54 mm header grid. Y and the adapter
    center-to-controller transform are provisional until checked on the physical
    assembly.
    """

    adapter_x = metadata["adapter_center_x"]
    return {
        "rst": (adapter_x + RST_LOCAL_X, BUTTON_LOCAL_Y),
        "boot": (adapter_x + BOOT_LOCAL_X, BUTTON_LOCAL_Y),
        "rgb": (adapter_x + RGB_LOCAL_X, RGB_LOCAL_Y),
    }


def _cover_latch_hook(
    *, x: float, y_sign: int, inner_half_width: float
) -> cq.Workplane:
    """One ramped inward hook that catches below the carrier edge."""

    inner_face = y_sign * inner_half_width
    tip = y_sign * (inner_half_width - COVER_LATCH_HOOK_DEPTH)
    if y_sign > 0:
        profile = [
            (inner_face, COVER_BOTTOM_Z + 0.10),
            (inner_face, COVER_LATCH_LEDGE_Z),
            (tip, COVER_LATCH_LEDGE_Z),
        ]
    else:
        profile = [
            (inner_face, COVER_BOTTOM_Z + 0.10),
            (tip, COVER_LATCH_LEDGE_Z),
            (inner_face, COVER_LATCH_LEDGE_Z),
        ]
    return (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(COVER_LATCH_WIDTH / 2.0, both=True)
        .translate((x, 0, 0))
    )


def make_cover() -> tuple[cq.Workplane, dict[str, object]]:
    """Build the low-profile snap cover in its assembled orientation."""

    _, carrier_metadata = make_base()
    inner_length = carrier_metadata["total_length"] + 2.0 * COVER_XY_CLEARANCE
    inner_width = carrier_metadata["total_width"] + 2.0 * COVER_XY_CLEARANCE
    outer_length = inner_length + 2.0 * COVER_WALL
    outer_width = inner_width + 2.0 * COVER_WALL
    cover_height = COVER_TOP_Z - COVER_BOTTOM_Z

    outer = rounded_box_xy(
        outer_length,
        outer_width,
        cover_height,
        COVER_CORNER_RADIUS,
    ).translate((0, 0, COVER_BOTTOM_Z))
    cavity = rounded_box_xy(
        inner_length,
        inner_width,
        COVER_ROOF_UNDERSIDE_Z - COVER_BOTTOM_Z + 0.15,
        CORNER_RADIUS,
    ).translate((0, 0, COVER_BOTTOM_Z - 0.15))
    cover = outer.cut(cavity)

    # Two bounded apertures preserve the lower +X end wall and a 2 mm center
    # rib. Each has a short 12 mm roof-down bridge; slicer bridge settings must
    # be checked on the first print. Port positions remain first-fit estimates.
    usb_cut_height = USB_PORT_HEIGHT + 0.10
    for y_sign in (-1, 1):
        usb_port = (
            cq.Workplane("XY")
            .center(
                outer_length / 2.0,
                y_sign * USB_PORT_CENTER_Y,
            )
            .box(
                2.0 * COVER_WALL + 2.0,
                USB_PORT_WIDTH,
                usb_cut_height,
                centered=(True, True, False),
            )
            .translate(
                (
                    0,
                    0,
                    USB_PORT_CENTER_Z - usb_cut_height / 2.0,
                )
            )
        )
        cover = cover.cut(usb_port)

    latch_centers_x = (-48.0, 42.0)
    inner_half_width = inner_width / 2.0
    for y_sign in (-1, 1):
        wall_y = y_sign * (inner_half_width + COVER_WALL / 2.0)
        for latch_x in latch_centers_x:
            # Two cuts turn the lower wall into a compliant tongue.
            for x_sign in (-1, 1):
                slot_x = latch_x + x_sign * (
                    COVER_LATCH_WIDTH / 2.0 + COVER_LATCH_SLOT / 2.0
                )
                relief_slot = (
                    cq.Workplane("XY")
                    .center(slot_x, wall_y)
                    .box(
                        COVER_LATCH_SLOT,
                        COVER_WALL + 1.0,
                        COVER_LATCH_RELIEF_TOP_Z - COVER_BOTTOM_Z + 0.20,
                        centered=(True, True, False),
                    )
                    .translate((0, 0, COVER_BOTTOM_Z - 0.10))
                )
                cover = cover.cut(relief_slot)

            cover = cover.union(
                _cover_latch_hook(
                    x=latch_x,
                    y_sign=y_sign,
                    inner_half_width=inner_half_width,
                )
            )
            stop_y = y_sign * (
                inner_half_width - COVER_LATCH_STOP_DEPTH / 2.0
            )
            upper_stop = (
                cq.Workplane("XY")
                .center(latch_x, stop_y)
                .box(
                    COVER_LATCH_WIDTH,
                    COVER_LATCH_STOP_DEPTH,
                    COVER_LATCH_STOP_HEIGHT,
                    centered=(True, True, False),
                )
                .translate((0, 0, COVER_LATCH_STOP_BOTTOM_Z))
            )
            cover = cover.union(upper_stop)

    controls = controller_control_locations(carrier_metadata)
    for control_name in ("rst", "boot"):
        x, y = controls[control_name]
        tool_hole = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(BUTTON_TOOL_HOLE_DIAMETER / 2.0)
            .extrude(COVER_ROOF + 0.60)
            .translate((0, 0, COVER_ROOF_UNDERSIDE_Z - 0.30))
        )
        cover = cover.cut(tool_hole)

    # The light well opens only to the inside. A 0.45 mm exterior skin remains
    # so white PETG/PLA can diffuse the onboard RGB status LED.
    rgb_x, rgb_y = controls["rgb"]
    light_well = (
        cq.Workplane("XY")
        .center(rgb_x, rgb_y)
        .circle(RGB_LIGHT_WELL_DIAMETER / 2.0)
        .extrude(COVER_ROOF - RGB_MEMBRANE_THICKNESS + 0.05)
        .translate((0, 0, COVER_ROOF_UNDERSIDE_Z - 0.05))
    )
    cover = cover.cut(light_well)

    cover_metadata: dict[str, object] = {
        "inner_length": inner_length,
        "inner_width": inner_width,
        "outer_length": outer_length,
        "outer_width": outer_width,
        "bottom_z": COVER_BOTTOM_Z,
        "top_z": COVER_TOP_Z,
        "roof_underside_z": COVER_ROOF_UNDERSIDE_Z,
        "latch_centers_x": latch_centers_x,
        "usb_port_centers_y": (-USB_PORT_CENTER_Y, USB_PORT_CENTER_Y),
        "usb_port_width": USB_PORT_WIDTH,
        "usb_port_height": USB_PORT_HEIGHT,
        "usb_port_center_z": USB_PORT_CENTER_Z,
        "usb_port_origin_status": USB_PORT_ORIGIN_STATUS,
        "controls": controls,
        "control_origin_status": "first_fit_unverified_adapter_origin",
    }
    return cover.clean(), cover_metadata


def orient_cover_roof_down(shape: cq.Workplane) -> cq.Workplane:
    """Rotate the cover to its support-free print orientation at Z=0."""

    oriented = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    return oriented.translate((0, 0, -oriented.val().BoundingBox().zmin))


def make_cover_latch_coupon() -> cq.Workplane:
    """Extract one real latch segment for a quick print-on-carrier fit check."""

    cover, metadata = make_cover()
    latch_x = metadata["latch_centers_x"][0]
    outer_width = float(metadata["outer_width"])
    clip_region = (
        cq.Workplane("XY")
        .center(latch_x, outer_width / 2.0 - 5.0)
        .box(
            COVER_LATCH_WIDTH + 8.0,
            14.0,
            COVER_TOP_Z - COVER_BOTTOM_Z + 2.0,
            centered=(True, True, False),
        )
        .translate((0, 0, COVER_BOTTOM_Z - 1.0))
    )
    return cover.intersect(clip_region).clean()


def make_pn532_fit_coupon() -> cq.Workplane:
    """Small print-first coupon that tests width, clearance, and clip flex."""

    coupon_length = 18.0
    coupon_width = PN532.width + 2.0 * (CLEARANCE_PER_SIDE + CLIP_WALL + 2.0)
    coupon = rounded_box_xy(coupon_length, coupon_width, BASE_THICKNESS)
    for y_sign in (-1, 1):
        coupon = coupon.union(pn532_side_clip(x=0.0, y_sign=y_sign))
    for x in (-5.0, 5.0):
        support = (
            cq.Workplane("XY")
            .center(x, 0)
            .box(2.5, PN532.width - 4.0, PN532_STANDOFF, centered=(True, True, False))
            .translate((0, 0, BASE_THICKNESS))
        )
        coupon = coupon.union(support)
    return coupon.clean()


def make_screw_fit_coupon() -> cq.Workplane:
    """Three pilot widths for a low-risk M2.5 self-tapping fit test."""

    coupon = rounded_box_xy(42.0, 15.0, BASE_THICKNESS)
    for x, pilot_width in zip((-12.0, 0.0, 12.0), (1.90, 2.10, 2.30)):
        boss = (
            cq.Workplane("XY")
            .center(x, 0)
            .circle(MOUNT_BOSS_DIAMETER / 2.0)
            .extrude(ADAPTER_STANDOFF)
            .translate((0, 0, BASE_THICKNESS))
        )
        pilot = (
            cq.Workplane("XY")
            .center(x, 0)
            .slot2D(SELF_TAP_SLOT_LENGTH, pilot_width)
            .extrude(SELF_TAP_DEPTH + 0.20)
            .translate((0, 0, BASE_THICKNESS + ADAPTER_STANDOFF - SELF_TAP_DEPTH))
        )
        coupon = coupon.union(boss.cut(pilot))
    return coupon.clean()


def board_envelope(board: Board, center_x: float, z: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .center(center_x, 0)
        .box(board.length, board.width, board.thickness, centered=(True, True, False))
        .translate((0, 0, z))
    )


def export() -> None:
    output = Path(__file__).resolve().parent / "exports"
    output.mkdir(parents=True, exist_ok=True)

    base, metadata = make_base()
    cover, cover_metadata = make_cover()
    printable_cover = orient_cover_roof_down(cover)
    latch_coupon = make_cover_latch_coupon()
    printable_latch_coupon = orient_cover_roof_down(latch_coupon)
    coupon = make_pn532_fit_coupon()
    screw_coupon = make_screw_fit_coupon()
    generated = (
        base,
        cover,
        printable_cover,
        latch_coupon,
        printable_latch_coupon,
        coupon,
        screw_coupon,
    )
    if not all(shape.val().isValid() for shape in generated):
        raise RuntimeError("Generated carrier, cover, or fit coupons are not valid solids")

    cq.exporters.export(base, str(output / "openspool_s3_pn532_carrier.stl"), tolerance=0.02)
    cq.exporters.export(base, str(output / "openspool_s3_pn532_carrier.step"))
    cq.exporters.export(
        printable_cover,
        str(output / "openspool_s3_pn532_snap_cover.stl"),
        tolerance=0.02,
    )
    cq.exporters.export(cover, str(output / "openspool_s3_pn532_snap_cover.step"))
    cq.exporters.export(
        printable_latch_coupon,
        str(output / "snap_cover_latch_fit_coupon.stl"),
        tolerance=0.02,
    )
    cq.exporters.export(
        latch_coupon,
        str(output / "snap_cover_latch_fit_coupon.step"),
    )
    cq.exporters.export(coupon, str(output / "pn532_clip_fit_coupon.stl"), tolerance=0.02)
    cq.exporters.export(coupon, str(output / "pn532_clip_fit_coupon.step"))
    cq.exporters.export(screw_coupon, str(output / "m2p5_screw_fit_coupon.stl"), tolerance=0.02)
    cq.exporters.export(screw_coupon, str(output / "m2p5_screw_fit_coupon.step"))

    preview_svg = cq.exporters.getSVG(
        base.val(),
        opts={
            "width": 1200,
            "height": 720,
            "marginLeft": 60,
            "marginTop": 45,
            "projectionDir": (1.0, -1.0, 0.72),
            "showAxes": False,
            "showHidden": True,
            "strokeWidth": 0.7,
            "strokeColor": (28, 38, 50),
            "hiddenColor": (116, 129, 145),
        },
    )
    preview_svg_path = output / "openspool_s3_pn532_carrier_preview.svg"
    preview_svg_path.write_bytes(preview_svg.replace("\r\n", "\n").encode("utf-8"))
    cairosvg.svg2png(
        bytestring=preview_svg.encode("utf-8"),
        write_to=str(output / "openspool_s3_pn532_carrier_preview.png"),
        output_width=1600,
        output_height=960,
        background_color="#f4f6f8",
    )

    cover_preview_svg = cq.exporters.getSVG(
        cover.val(),
        opts={
            "width": 1200,
            "height": 720,
            "marginLeft": 60,
            "marginTop": 45,
            "projectionDir": (1.0, -1.0, 0.72),
            "showAxes": False,
            "showHidden": True,
            "strokeWidth": 0.7,
            "strokeColor": (28, 38, 50),
            "hiddenColor": (116, 129, 145),
        },
    )
    cover_preview_svg_path = output / "openspool_s3_pn532_snap_cover_preview.svg"
    cover_preview_svg_path.write_bytes(
        cover_preview_svg.replace("\r\n", "\n").encode("utf-8")
    )
    cairosvg.svg2png(
        bytestring=cover_preview_svg.encode("utf-8"),
        write_to=str(output / "openspool_s3_pn532_snap_cover_preview.png"),
        output_width=1600,
        output_height=960,
        background_color="#f4f6f8",
    )

    assembly = cq.Assembly(name="OpenSpool carrier, cover, and hardware fit check")
    assembly.add(base, name="printable_carrier", color=cq.Color(0.12, 0.25, 0.42))
    pn532_z = BASE_THICKNESS + PN532_STANDOFF
    adapter_z = BASE_THICKNESS + ADAPTER_STANDOFF
    assembly.add(
        board_envelope(PN532, metadata["pn532_center_x"], pn532_z),
        name="PN532_42p7x40p4_envelope",
        color=cq.Color(0.72, 0.08, 0.08, 0.75),
    )
    assembly.add(
        board_envelope(TERMINAL_ADAPTER, metadata["adapter_center_x"], adapter_z),
        name="terminal_adapter_80x70_envelope",
        color=cq.Color(0.03, 0.45, 0.20, 0.65),
    )
    assembly.add(
        board_envelope(
            ESP32,
            metadata["adapter_center_x"],
            adapter_z + TERMINAL_ADAPTER.thickness + ESP32_SOCKET_HEIGHT,
        ),
        name="AITRIP_YD_ESP32_S3_63x28_envelope",
        color=cq.Color(0.05, 0.12, 0.18, 0.80),
    )
    assembly.add(
        cover,
        name="printable_snap_cover_first_fit",
        color=cq.Color(0.92, 0.95, 0.98, 0.35),
    )
    assembly.save(str(output / "openspool_s3_pn532_fit_check.step"))

    print("OpenSpool terminal-adapter + PN532 carrier")
    print(
        f"overall: {metadata['total_length']:.2f} x "
        f"{metadata['total_width']:.2f} x {metadata['total_height']:.2f} mm"
    )
    print(
        f"adapter mounting pattern: {ADAPTER_HOLE_PITCH_X:.2f} x "
        f"{ADAPTER_HOLE_PITCH_Y:.2f} mm; {FASTENER_THREAD} self-tapping slots"
    )
    print(f"solid volume: {base.val().Volume():.2f} mm^3")
    print(
        f"cover: {cover_metadata['outer_length']:.2f} x "
        f"{cover_metadata['outer_width']:.2f} x "
        f"{COVER_TOP_Z - COVER_BOTTOM_Z:.2f} mm; "
        f"volume {cover.val().Volume():.2f} mm^3"
    )
    for path in sorted(output.iterdir()):
        print(path.name)


if __name__ == "__main__":
    export()
