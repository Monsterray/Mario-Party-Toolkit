"""Opt-in local hooks for deterministic GUI inspection."""

import argparse
import json
from pathlib import Path

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QTabWidget, QWidget


class UITestHooks:
    """Drive and inspect the GUI without changing normal launches."""

    @staticmethod
    def parse_args(argv):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument("--mpt-test-game")
        parser.add_argument("--mpt-test-tab")
        parser.add_argument("--mpt-test-screenshot", type=Path)
        parser.add_argument("--mpt-test-dump", type=Path)
        parser.add_argument("--mpt-test-quit-after", type=int, default=1000)
        return parser.parse_known_args(argv)[0]

    @staticmethod
    def install(window, argv):
        options = UITestHooks.parse_args(argv)
        if not any((options.mpt_test_game, options.mpt_test_tab,
                    options.mpt_test_screenshot, options.mpt_test_dump)):
            return

        def capture():
            """Capture after navigation and Qt have completed their layouts."""
            page = window.findChild(QWidget, f"{options.mpt_test_game}Page") if options.mpt_test_game else None
            tab_widget = page.findChild(QTabWidget) if page else None
            if tab_widget and options.mpt_test_tab:
                target = options.mpt_test_tab.casefold()
                for index in range(tab_widget.count()):
                    if tab_widget.tabText(index).casefold() == target:
                        tab_widget.setCurrentIndex(index)
                        break

            if options.mpt_test_dump:
                options.mpt_test_dump.parent.mkdir(parents=True, exist_ok=True)
                options.mpt_test_dump.write_text(
                    json.dumps(UITestHooks.layout_snapshot(window), indent=2) + "\n",
                    encoding="utf-8",
                )
            if options.mpt_test_screenshot:
                options.mpt_test_screenshot.parent.mkdir(parents=True, exist_ok=True)
                window.grab().save(str(options.mpt_test_screenshot))

        def navigate_then_capture():
            if options.mpt_test_game:
                window.navigationInterface.setCurrentItem(options.mpt_test_game)
            QTimer.singleShot(750, capture)

        QTimer.singleShot(250, navigate_then_capture)
        QTimer.singleShot(max(1500, options.mpt_test_quit_after),
                          QApplication.instance().quit)

    @staticmethod
    def layout_snapshot(window):
        snapshot = {"window": [window.width(), window.height()], "tabs": [], "switches": []}
        for tab_widget in window.findChildren(QTabWidget):
            bar = tab_widget.tabBar()
            snapshot["tabs"].append({
                "page": tab_widget.parentWidget().objectName(),
                "bar_geometry": [bar.x(), bar.y(), bar.width(), bar.height()],
                "stylesheet_tab_bar": next(
                    (line.strip() for line in tab_widget.styleSheet().splitlines()
                     if "alignment:" in line),
                    None,
                ),
                "items": [
                    {"text": tab_widget.tabText(i), "rect": [
                        bar.tabRect(i).x(), bar.tabRect(i).y(),
                        bar.tabRect(i).width(), bar.tabRect(i).height(),
                    ]}
                    for i in range(tab_widget.count())
                ],
            })

        for widget in window.findChildren(QWidget):
            if widget.__class__.__name__ == "Indicator":
                snapshot["switches"].append({
                    "rect": [widget.x(), widget.y(), widget.width(), widget.height()],
                    "parent": widget.parentWidget().__class__.__name__,
                })
        return snapshot
