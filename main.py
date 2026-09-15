# ============================================
# Mario Party Toolkit
# Author: Tabitha Hanegan (tabitha@tabs.gay)
# Date: 09/30/2025
# License: MIT
# ============================================

import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5.QtCore import Qt
from qfluentwidgets import FluentTranslator, setFontFamilies

from components.mario_party_toolkit import MarioPartyToolkit
from utils.resource_manager import ResourceManager
from utils.scale_manager import ScaleManager
from version import versionString


def main():
    # Enable High DPI support for sharp rendering
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)

    system_font = QFontDatabase.systemFont(QFontDatabase.GeneralFont)
    setFontFamilies([system_font.family()])
    
    # Now calculate auto-scale based on display (after QApplication is created)
    scale_factor = ScaleManager.calculate_auto_scale()
    ScaleManager.set_scale_factor(scale_factor)
    print(f"✓ UI scale: {int(scale_factor * 100)}%")
    
    # Set application-wide icon
    icon_path = ResourceManager.get_resource_path("assets/icons/diceBlock.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(str(icon_path)))
        print("✓ Application icon set")
    else:
        print("⚠️  Icon file not found")
    
    # Add translator for internationalization
    translator = FluentTranslator()
    app.installTranslator(translator)
    
    # Set application-wide font with scaled size
    base_font_size = 9
    scaled_font_size = ScaleManager.get_scaled_font_size(base_font_size, scale_factor)
    font = system_font
    font.setPointSize(scaled_font_size)
    app.setFont(font)
    
    if scale_factor != 1.0:
        print(f"✓ Font size scaled: {base_font_size}pt → {scaled_font_size}pt")
    
    # Create and show the main window
    window = MarioPartyToolkit()
    ScaleManager.scale_widget_tree(window, scale_factor)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
