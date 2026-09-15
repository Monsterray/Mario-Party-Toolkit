import unittest

from PyQt5.QtWidgets import QApplication, QTabWidget, QWidget

from utils.ui_test_hooks import UITestHooks


class UITestHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_layout_snapshot_reports_tab_geometry(self):
        window = QWidget()
        page = QWidget(window)
        page.setObjectName("marioParty2Page")
        tabs = QTabWidget(page)
        tabs.addTab(QWidget(), "Minigame Replacement")
        tabs.resize(400, 200)
        window.resize(500, 300)
        window.show()
        self.app.processEvents()

        snapshot = UITestHooks.layout_snapshot(window)
        self.assertEqual(snapshot["window"], [500, 300])
        self.assertEqual(snapshot["tabs"][0]["items"][0]["text"], "Minigame Replacement")
        self.assertGreater(snapshot["tabs"][0]["items"][0]["rect"][2], 0)


if __name__ == "__main__":
    unittest.main()
