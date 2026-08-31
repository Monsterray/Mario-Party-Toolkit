# ============================================
# Mario Party Toolkit
# Author: Tabitha Hanegan (tabitha@tabs.gay)
# Date: 09/30/2025
# License: MIT
# ============================================

"""Helpers for randomizing item/orb odds and prices."""

import random

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QMessageBox
from qfluentwidgets import BodyLabel, LineEdit, PushButton, SubtitleLabel


def random_weights(count, total=100):
    """Return `count` non-negative integers that sum to `total`."""
    if count <= 0:
        return []
    if count == 1:
        return [total]

    # Breakpoints on [0, total] create count positive-length segments
    cuts = sorted(random.randint(0, total) for _ in range(count - 1))
    points = [0] + cuts + [total]
    return [points[i + 1] - points[i] for i in range(count)]


def random_price(min_price=3, max_price=30):
    """Return a random shop price within the given range."""
    if min_price > max_price:
        min_price, max_price = max_price, min_price
    return random.randint(min_price, max_price)


def apply_weights_to_entries(entries, total=100):
    """Fill LineEdit widgets with random weights that sum to `total`."""
    live = []
    for entry in entries:
        try:
            # Touch the widget to ensure it wasn't deleted
            _ = entry.text()
            live.append(entry)
        except RuntimeError:
            continue

    if not live:
        return

    weights = random_weights(len(live), total)
    for entry, weight in zip(live, weights):
        entry.setText(str(weight))


def prompt_price_range(parent=None, default_min=3, default_max=30):
    """
    Show a dialog asking for min/max price.
    Returns (min_price, max_price) on OK, or None if cancelled.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle("Randomize Options")
    dialog.setModal(True)
    dialog.setMinimumWidth(320)

    layout = QVBoxLayout(dialog)
    layout.setSpacing(12)
    layout.setContentsMargins(20, 16, 20, 16)

    title = SubtitleLabel("Price Range")
    title.setAlignment(Qt.AlignCenter)
    layout.addWidget(title)

    desc = BodyLabel("Random prices will be chosen between these values:")
    desc.setAlignment(Qt.AlignCenter)
    layout.addWidget(desc)

    fields = QHBoxLayout()
    fields.setSpacing(12)

    min_col = QVBoxLayout()
    min_col.setSpacing(4)
    min_col.addWidget(BodyLabel("Min Price"))
    min_entry = LineEdit()
    min_entry.setText(str(default_min))
    min_entry.setPlaceholderText("Min")
    min_col.addWidget(min_entry)
    fields.addLayout(min_col)

    max_col = QVBoxLayout()
    max_col.setSpacing(4)
    max_col.addWidget(BodyLabel("Max Price"))
    max_entry = LineEdit()
    max_entry.setText(str(default_max))
    max_entry.setPlaceholderText("Max")
    max_col.addWidget(max_entry)
    fields.addLayout(max_col)

    layout.addLayout(fields)

    buttons = QHBoxLayout()
    buttons.setSpacing(8)
    buttons.addStretch()

    cancel_btn = PushButton("Cancel")
    cancel_btn.clicked.connect(dialog.reject)
    buttons.addWidget(cancel_btn)

    ok_btn = PushButton("Randomize")
    ok_btn.setDefault(True)
    buttons.addWidget(ok_btn)
    layout.addLayout(buttons)

    result = {"range": None}

    def on_accept():
        try:
            min_price = int(min_entry.text().strip())
            max_price = int(max_entry.text().strip())
        except (ValueError, TypeError):
            QMessageBox.warning(dialog, "Invalid Input", "Min and max price must be whole numbers.")
            return

        if min_price < 0 or max_price < 0:
            QMessageBox.warning(dialog, "Invalid Input", "Prices cannot be negative.")
            return

        if min_price > max_price:
            QMessageBox.warning(dialog, "Invalid Input", "Min price cannot be greater than max price.")
            return

        result["range"] = (min_price, max_price)
        dialog.accept()

    ok_btn.clicked.connect(on_accept)

    if dialog.exec_() != QDialog.Accepted:
        return None
    return result["range"]
