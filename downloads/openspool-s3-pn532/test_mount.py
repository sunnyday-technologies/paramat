"""Geometry checks for the OpenSpool terminal-adapter + PN532 carrier."""

from __future__ import annotations

import unittest

import openspool_s3_pn532_mount as model


class CarrierGeometryTests(unittest.TestCase):
    def test_carrier_and_coupons_are_valid_and_a1_mini_sized(self) -> None:
        carrier, metadata = model.make_base()
        self.assertTrue(carrier.val().isValid())
        self.assertTrue(model.make_pn532_fit_coupon().val().isValid())
        self.assertTrue(model.make_screw_fit_coupon().val().isValid())
        self.assertGreater(carrier.val().Volume(), 25_000.0)
        self.assertLess(metadata["total_length"], 180.0)
        self.assertLess(metadata["total_width"], 180.0)

    def test_reported_envelopes_match_target_hardware(self) -> None:
        self.assertEqual((64.20, 28.20), (model.ESP32.length, model.ESP32.width))
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


if __name__ == "__main__":
    unittest.main()
