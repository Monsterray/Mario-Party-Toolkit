import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QApplication, QTabWidget, QWidget

from pages.mario_party_pages import MarioPartyPages, TextSizedTabBar


class TabStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_tabs_center_and_size_to_their_text(self):
        pages = MarioPartyPages()
        tab_widget = QTabWidget()
        tab_widget.setTabBar(TextSizedTabBar(tab_widget))
        pages.apply_tab_style(tab_widget)
        tab_widget.addTab(QWidget(), "Coins")
        tab_widget.addTab(QWidget(), "Minigame Replacement")
        tab_widget.resize(1000, 400)
        tab_widget.show()
        self.app.processEvents()

        tab_bar = tab_widget.tabBar()
        self.assertFalse(tab_bar.expanding())
        self.assertEqual(tab_bar.elideMode(), Qt.ElideNone)
        self.assertTrue(tab_bar.usesScrollButtons())
        self.assertEqual(tab_bar.tabRect(1).width(), tab_bar.tabRect(0).width())
        self.assertGreaterEqual(
            tab_bar.tabRect(0).width(),
            QFontMetrics(tab_bar.font()).horizontalAdvance("Minigame Replacement") + 24,
        )
        self.assertIn("alignment: center", tab_widget.styleSheet())
        self.assertNotIn("min-width", tab_widget.styleSheet())

    def test_tab_widths_fit_rendered_text(self):
        tab_widget = QTabWidget()
        tab_widget.setTabBar(TextSizedTabBar(tab_widget))
        tab_widget.addTab(QWidget(), "Minigame Replacement")
        tab_widget.show()
        self.app.processEvents()

        tab_bar = tab_widget.tabBar()
        needed = QFontMetrics(tab_bar.font()).horizontalAdvance(tab_bar.tabText(0))
        self.assertGreaterEqual(tab_bar.tabRect(0).width(), needed + 24)

    def test_overflow_tabs_stay_in_scroll_area(self):
        tab_widget = QTabWidget()
        tab_widget.setTabBar(TextSizedTabBar(tab_widget))
        pages = MarioPartyPages()
        pages.apply_tab_style(tab_widget)
        for label in (
            "Coins Mods",
            "Item Prices",
            "Item Replacement",
            "Minigame Replacement",
            "Star Handicaps",
            "Bonus Star Replacement",
        ):
            tab_widget.addTab(QWidget(), label)

        tab_widget.resize(300, 400)
        tab_widget.show()
        self.app.processEvents()

        tab_bar = tab_widget.tabBar()
        self.assertIn("alignment: left", tab_widget.styleSheet())
        self.assertGreaterEqual(tab_bar.tabRect(0).x(), 0)
        self.assertGreaterEqual(tab_bar.tabRect(0).width(), 200)


if __name__ == "__main__":
    unittest.main()
