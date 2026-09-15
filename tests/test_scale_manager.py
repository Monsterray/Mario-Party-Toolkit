import unittest

from PyQt5.QtWidgets import QApplication, QLabel, QWidget

from utils.scale_manager import ScaleManager


class ScaleManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_scale_rounds_dimensions_consistently(self):
        self.assertEqual(ScaleManager.scale(60, 0.75), 45)
        self.assertEqual(ScaleManager.get_scaled_font_size(9, 0.75), 7)

    def test_scale_stylesheet_scales_literal_pixels(self):
        self.assertEqual(
            ScaleManager.scale_stylesheet("padding: 16px; min-width: 80px;", 0.75),
            "padding: 12px; min-width: 60px;",
        )

    def test_scale_clamp_allows_smaller_displays(self):
        ScaleManager.set_scale_factor(0.25)
        self.assertEqual(ScaleManager.get_scale_factor(), 0.5)
        ScaleManager._scale_factor = None

    def test_scale_widget_tree_scales_fixed_widgets_and_styles(self):
        root = QWidget()
        label = QLabel(root)
        label.setFixedWidth(60)
        label.setStyleSheet("font-size: 16px; padding: 8px;")
        ScaleManager.scale_widget_tree(root, 0.75)
        self.assertEqual(label.minimumWidth(), 45)
        self.assertEqual(label.maximumWidth(), 45)
        self.assertIn("font-size: 12px", label.styleSheet())
        self.assertIn("padding: 6px", label.styleSheet())


if __name__ == "__main__":
    unittest.main()
