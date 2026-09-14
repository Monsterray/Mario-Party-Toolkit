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


def prompt_int_range(
    parent=None,
    *,
    title="Randomize Options",
    heading="Range",
    description="Random values will be chosen between these bounds:",
    min_label="Min",
    max_label="Max",
    default_min=1,
    default_max=10,
    allow_zero=True,
):
    """
    Show a dialog asking for min/max integers.
    Returns (min_value, max_value) on OK, or None if cancelled.
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setModal(True)
    dialog.setMinimumWidth(320)

    layout = QVBoxLayout(dialog)
    layout.setSpacing(12)
    layout.setContentsMargins(20, 16, 20, 16)

    heading_label = SubtitleLabel(heading)
    heading_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(heading_label)

    desc = BodyLabel(description)
    desc.setAlignment(Qt.AlignCenter)
    layout.addWidget(desc)

    fields = QHBoxLayout()
    fields.setSpacing(12)

    min_col = QVBoxLayout()
    min_col.setSpacing(4)
    min_col.addWidget(BodyLabel(min_label))
    min_entry = LineEdit()
    min_entry.setText(str(default_min))
    min_entry.setPlaceholderText("Min")
    min_col.addWidget(min_entry)
    fields.addLayout(min_col)

    max_col = QVBoxLayout()
    max_col.setSpacing(4)
    max_col.addWidget(BodyLabel(max_label))
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
            min_value = int(min_entry.text().strip())
            max_value = int(max_entry.text().strip())
        except (ValueError, TypeError):
            QMessageBox.warning(dialog, "Invalid Input", "Min and max must be whole numbers.")
            return

        if allow_zero:
            if min_value < 0 or max_value < 0:
                QMessageBox.warning(dialog, "Invalid Input", "Values cannot be negative.")
                return
        else:
            if min_value < 1 or max_value < 1:
                QMessageBox.warning(dialog, "Invalid Input", "Values must be at least 1.")
                return

        if min_value > max_value:
            QMessageBox.warning(dialog, "Invalid Input", "Min cannot be greater than max.")
            return

        result["range"] = (min_value, max_value)
        dialog.accept()

    ok_btn.clicked.connect(on_accept)

    if dialog.exec_() != QDialog.Accepted:
        return None
    return result["range"]


def prompt_price_range(parent=None, default_min=3, default_max=30):
    """
    Show a dialog asking for min/max price.
    Returns (min_price, max_price) on OK, or None if cancelled.
    """
    return prompt_int_range(
        parent,
        title="Randomize Prices",
        heading="Price Range",
        description="Random prices will be chosen between these values:",
        min_label="Min Price",
        max_label="Max Price",
        default_min=default_min,
        default_max=default_max,
    )


def prompt_weight_range(parent=None, default_min=0, default_max=100):
    """
    Show a dialog asking for min/max weight.
    Returns (min_weight, max_weight) on OK, or None if cancelled.
    """
    return prompt_int_range(
        parent,
        title="Randomize Weights",
        heading="Weight Range",
        description="Random weights will be chosen between these values:",
        min_label="Min Weight",
        max_label="Max Weight",
        default_min=default_min,
        default_max=default_max,
    )
