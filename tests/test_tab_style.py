import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTabWidget, QWidget

from pages.mario_party_pages import MarioPartyPages


class TabStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_tabs_center_and_size_to_their_text(self):
        pages = MarioPartyPages()
        tab_widget = QTabWidget()
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
        self.assertGreater(tab_bar.tabRect(1).width(), tab_bar.tabRect(0).width())
        self.assertIn("alignment: center", tab_widget.styleSheet())
        self.assertNotIn("min-width", tab_widget.styleSheet())


if __name__ == "__main__":
    unittest.main()
