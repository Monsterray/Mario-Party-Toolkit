# ============================================
# Mario Party Toolkit
# Author: Tabitha Hanegan (tabitha@tabs.gay)
# Date: 10/13/2025
# License: MIT
# ============================================

import re

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication


class ScaleManager:
    """Manages UI scaling - automatically calculated based on display size"""
    
    # Base resolution for 100% scaling (1920x1080 is standard Full HD)
    BASE_WIDTH = 1920
    BASE_HEIGHT = 1080
    
    DEFAULT_SCALE = 1.0
    _scale_factor = None
    
    @staticmethod
    def calculate_auto_scale():
        """Automatically calculate scale factor based on display size"""
        try:
            # Try to get the primary screen
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    screen_width = screen_geometry.width()
                    screen_height = screen_geometry.height()
                    
                    # Calculate scale based on screen dimensions
                    # Use the smaller ratio to ensure everything fits
                    width_ratio = screen_width / ScaleManager.BASE_WIDTH
                    height_ratio = screen_height / ScaleManager.BASE_HEIGHT
                    
                    # Use the smaller ratio and round to nearest 0.25
                    auto_scale = min(width_ratio, height_ratio)
                    auto_scale = round(auto_scale * 4) / 4  # Round to nearest 0.25
                    
                    # Keep small displays usable; widget dimensions are scaled
                    # after construction so this applies consistently.
                    auto_scale = max(0.5, min(3.0, auto_scale))
                    
                    print(f"✓ Auto-calculated scale: {auto_scale} (Display: {screen_width}x{screen_height})")
                    return auto_scale
        except Exception as e:
            print(f"⚠️  Error calculating auto scale: {e}")
        
        return ScaleManager.DEFAULT_SCALE
    
    @staticmethod
    def get_scale_factor():
        """Return this process's scale; never reuse a stale display value."""
        if ScaleManager._scale_factor is None:
            ScaleManager._scale_factor = ScaleManager.calculate_auto_scale()
        return ScaleManager._scale_factor

    @staticmethod
    def set_scale_factor(scale_factor):
        ScaleManager._scale_factor = max(0.5, min(3.0, float(scale_factor)))

    @staticmethod
    def scale(value, scale_factor=None):
        scale_factor = scale_factor or ScaleManager.get_scale_factor()
        return max(1, round(float(value) * scale_factor)) if value else 0

    @staticmethod
    def scale_stylesheet(stylesheet, scale_factor=None):
        """Scale literal px values in local stylesheets exactly once."""
        scale_factor = scale_factor or ScaleManager.get_scale_factor()

        def replace(match):
            value = float(match.group(1))
            scaled = round(value * scale_factor)
            return f"{max(1, scaled) if value else 0}px"

        return re.sub(r"(?<![A-Za-z])([0-9]+(?:\.[0-9]+)?)px", replace, stylesheet)

    @staticmethod
    def scale_widget_tree(root, scale_factor=None):
        """Scale finite widget bounds and local stylesheets once."""
        scale_factor = scale_factor or ScaleManager.get_scale_factor()
        for widget in [root, *root.findChildren(QObject)]:
            if not hasattr(widget, "property") or widget.property("mptScaled"):
                continue
            # qfluentwidgets' switch indicator is custom-painted with fixed
            # 42x22 geometry and fixed slider coordinates; do not shrink it
            # without also rewriting the third-party paint implementation.
            if (widget.__class__.__module__.startswith("qfluentwidgets") and
                    widget.__class__.__name__ in {"Indicator", "SwitchButton"}):
                widget.setProperty("mptScaled", True)
                continue
            if hasattr(widget, "minimumWidth"):
                minimum = widget.minimumSize()
                maximum = widget.maximumSize()
                if minimum.width() or minimum.height():
                    widget.setMinimumSize(ScaleManager.scale(minimum.width(), scale_factor), ScaleManager.scale(minimum.height(), scale_factor))
                if maximum.width() < 16777215 or maximum.height() < 16777215:
                    widget.setMaximumSize(
                        ScaleManager.scale(maximum.width(), scale_factor) if maximum.width() < 16777215 else maximum.width(),
                        ScaleManager.scale(maximum.height(), scale_factor) if maximum.height() < 16777215 else maximum.height(),
                    )
            stylesheet = widget.styleSheet() if hasattr(widget, "styleSheet") else ""
            if stylesheet:
                widget.setStyleSheet(ScaleManager.scale_stylesheet(stylesheet, scale_factor))
            widget.setProperty("mptScaled", True)

    @staticmethod
    def get_scale_percentage():
        """Get the current scale as a percentage string (e.g., '100%')"""
        scale = ScaleManager.get_scale_factor()
        return f"{int(scale * 100)}%"
    
    @staticmethod
    def get_scaled_font_size(base_size, scale_factor=None):
        """Get scaled font size"""
        if scale_factor is None:
            scale_factor = ScaleManager.get_scale_factor()
        return max(1, round(base_size * scale_factor))
