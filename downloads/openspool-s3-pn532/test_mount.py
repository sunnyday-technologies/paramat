"""Geometry checks for the OpenSpool terminal-adapter + PN532 carrier."""

from __future__ import annotations

import unittest

import openspool_s3_pn532_mount as model


class CarrierGeometryTests(unittest.TestCase):
    def test_carrier_and_coupons_are_valid_and_a1_mini_sized(self) -> None:
        carrier, metadata = model.make_base()
        cover, cover_metadata = model.make_cover()
        self.assertTrue(carrier.val().isValid())
        self.assertTrue(cover.val().isValid())
        self.assertTrue(model.make_cover_latch_coupon().val().isValid())
        self.assertTrue(model.make_pn532_fit_coupon().val().isValid())
        self.assertTrue(model.make_screw_fit_coupon().val().isValid())
        self.assertGreater(carrier.val().Volume(), 25_000.0)
        self.assertGreater(cover.val().Volume(), 25_000.0)
        self.assertLess(metadata["total_length"], 180.0)
        self.assertLess(metadata["total_width"], 180.0)
        self.assertLess(cover_metadata["outer_length"], 180.0)
        self.assertLess(cover_metadata["outer_width"], 180.0)

    def test_reported_envelopes_match_target_hardware(self) -> None:
        self.assertEqual((63.00, 28.00), (model.ESP32.length, model.ESP32.width))
        self.assertEqual(
            (80.00, 70.00),
            (model.TERMINAL_ADAPTER.length, model.TERMINAL_ADAPTER.width),
        )
        self.assertEqual((42.70, 40.40), (model.PN532.length, model.PN532.width))

    def test_adapter_mounting_pattern_matches_published_board(self) -> None:
        self.assertEqual(72.50, model.ADAPTER_HOLE_PITCH_X)
        self.assertEqual(32.00, model.ADAPTER_HOLE_PITCH_Y)
        self.assertEqual("M2.5", model.FASTENER_THREAD)
        self.assertLess(model.SELF_TAP_SLOT_WIDTH, 2.50)
        self.assertGreater(model.SELF_TAP_DEPTH, 3.50)
        self.assertLessEqual(model.SELF_TAP_SLOT_LENGTH, 3.00)

    def test_pn532_clearance_and_rf_spacing_are_explicit(self) -> None:
        self.assertGreaterEqual(model.CLEARANCE_PER_SIDE, 0.40)
        self.assertGreaterEqual(model.BOARD_GAP, 12.00)
        self.assertGreaterEqual(model.TRUE_CLIP_OVERLAP, 0.30)
        self.assertLessEqual(model.TRUE_CLIP_OVERLAP, 0.50)
        self.assertGreaterEqual(
            model.BASE_THICKNESS + model.PN532_STANDOFF,
            8.00,
        )

    def test_layout_preserves_declared_board_gap(self) -> None:
        _, metadata = model.make_base()
        pn532_right = metadata["pn532_center_x"] + model.PN532.length / 2.0
        adapter_left = (
            metadata["adapter_center_x"] - model.TERMINAL_ADAPTER.length / 2.0
        )
        self.assertAlmostEqual(model.BOARD_GAP, adapter_left - pn532_right, places=6)

    def test_cover_clearance_groove_and_print_orientation(self) -> None:
        _, carrier = model.make_base()
        cover, metadata = model.make_cover()
        printable = model.orient_cover_roof_down(cover)
        printable_box = printable.val().BoundingBox()
        self.assertAlmostEqual(0.35, model.COVER_XY_CLEARANCE, places=6)
        self.assertAlmostEqual(
            carrier["total_length"] + 2.0 * model.COVER_XY_CLEARANCE,
            metadata["inner_length"],
            places=6,
        )
        self.assertAlmostEqual(
            carrier["total_width"] + 2.0 * model.COVER_XY_CLEARANCE,
            metadata["inner_width"],
            places=6,
        )
        self.assertAlmostEqual(1.60, model.COVER_WALL, places=6)
        self.assertAlmostEqual(1.60, model.COVER_ROOF, places=6)
        self.assertLess(model.COVER_LATCH_LEDGE_Z, 0.0)
        self.assertGreater(model.COVER_LATCH_STOP_BOTTOM_Z, model.BASE_THICKNESS)
        self.assertAlmostEqual(0.0, printable_box.zmin, places=6)
        self.assertAlmostEqual(
            model.COVER_TOP_Z - model.COVER_BOTTOM_Z,
            printable_box.zlen,
            places=6,
        )

    def test_control_apertures_follow_declared_pin_grid(self) -> None:
        _, carrier = model.make_base()
        _, cover = model.make_cover()
        controls = cover["controls"]
        adapter_x = carrier["adapter_center_x"]
        self.assertAlmostEqual(adapter_x - 5.08, controls["rst"][0], places=6)
        self.assertAlmostEqual(adapter_x, controls["boot"][0], places=6)
        self.assertAlmostEqual(adapter_x + 10.16, controls["rgb"][0], places=6)
        self.assertEqual(model.BUTTON_LOCAL_Y, controls["rst"][1])
        self.assertEqual(model.BUTTON_LOCAL_Y, controls["boot"][1])
        self.assertEqual(model.RGB_LOCAL_Y, controls["rgb"][1])
        self.assertEqual(4.20, model.BUTTON_TOOL_HOLE_DIAMETER)
        self.assertEqual(0.45, model.RGB_MEMBRANE_THICKNESS)
        self.assertEqual(
            "first_fit_unverified_adapter_origin",
            cover["control_origin_status"],
        )

    def test_closed_sides_and_two_bounded_usb_apertures(self) -> None:
        cover, metadata = model.make_cover()
        solid = cover.val()
        side_wall_y = metadata["inner_width"] / 2.0 + model.COVER_WALL / 2.0
        end_wall_x = metadata["outer_length"] / 2.0 - model.COVER_WALL / 2.0
        point = model.cq.Vector

        self.assertEqual((-7.00, 7.00), metadata["usb_port_centers_y"])
        self.assertEqual(12.00, metadata["usb_port_width"])
        self.assertEqual(9.00, metadata["usb_port_height"])
        self.assertEqual(20.50, metadata["usb_port_center_z"])
        self.assertEqual(
            "first_fit_unverified_controller_origin",
            metadata["usb_port_origin_status"],
        )
        self.assertAlmostEqual(
            2.00,
            2.0 * model.USB_PORT_CENTER_Y - model.USB_PORT_WIDTH,
            places=6,
        )
        self.assertAlmostEqual(
            model.COVER_ROOF_UNDERSIDE_Z,
            model.USB_PORT_CENTER_Z + model.USB_PORT_HEIGHT / 2.0,
            places=6,
        )

        # Both former service regions are solid. At +X, the center rib and
        # lower wall are solid while the two USB aperture centers are open.
        self.assertTrue(solid.isInside(point(30.0, side_wall_y, 17.0), 1e-6))
        self.assertTrue(solid.isInside(point(30.0, -side_wall_y, 17.0), 1e-6))
        self.assertTrue(solid.isInside(point(end_wall_x, 0.0, 20.5), 1e-6))
        self.assertTrue(solid.isInside(point(end_wall_x, 7.0, 8.0), 1e-6))
        self.assertFalse(solid.isInside(point(end_wall_x, 7.0, 20.5), 1e-6))
        self.assertFalse(solid.isInside(point(end_wall_x, -7.0, 20.5), 1e-6))


if __name__ == "__main__":
    unittest.main()
