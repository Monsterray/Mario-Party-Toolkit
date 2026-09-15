# ============================================
# Mario Party Toolkit
# Author: Tabitha Hanegan (tabitha@tabs.gay)
# Date: 09/30/2025
# License: MIT
# ============================================

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from qfluentwidgets import SubtitleLabel, BodyLabel, LineEdit, PushButton, TextEdit, CardWidget, ScrollArea, MessageBox
from functions import createDialog, fetchResource
from utils.code_validation import code_targets, validate_code_target
from utils.rom_identity import inspect_n64
from utils.injector_tools import resolve_tool
import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path


class InjectionWorker(QThread):
    """Worker thread for code injection to prevent UI freezing"""
    finished = pyqtSignal(bool, str)
    save_file_requested = pyqtSignal(str, str, str)  # extension, initial_name, file_types
    
    def __init__(self, file_path, codes_text, parent_widget):
        super().__init__()
        self.file_path = file_path
        self.codes_text = codes_text
        self.parent_widget = parent_widget
        self.save_file_path = None
    
    def run(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="mpt-inject-")
        work = Path(self.temp_dir.name)
        try:
            # Write codes to file
            codes_path = work / "codes.txt"
            with codes_path.open("w") as file:
                file.write("$MPToolkit\n" + self.codes_text)
            
            iso_path = self.file_path
            gameName = os.path.basename(iso_path)
            _, gameExt = os.path.splitext(gameName)
            
            # Handle different file types
            extension = Path(gameName).suffix.lower()
            if (extension == ".iso" and self.is_file_greater_than_4gb(iso_path)) or extension == ".wbfs":
                self.handle_wbfs_iso(iso_path, gameName, work, codes_path)
            elif extension == ".z64":
                self.handle_n64_rom(iso_path, gameName, work, codes_path)
            else:  # Regular ISO
                self.handle_regular_iso(iso_path, gameName, work, codes_path)
            
            self.finished.emit(True, "Code injection completed successfully!")

        except Exception as e:
            self.finished.emit(False, f"Error during injection: {str(e)}")
        finally:
            self.temp_dir.cleanup()

    def tool(self, name):
        """Resolve a bundled helper and report a useful macOS setup error."""
        return resolve_tool(name, fetchResource)
    
    def is_file_greater_than_4gb(self, file_path):
        file_size_bytes = os.path.getsize(file_path)
        file_size_gb = file_size_bytes / (1024**3)
        return file_size_gb > 4
    
    def is_file_less_than_100mb(self, file_path):
        file_size_bytes = os.path.getsize(file_path)
        file_size_mb = file_size_bytes / (1024**2)
        return file_size_mb < 100
    
    def handle_wbfs_iso(self, iso_path, gameName, work, codes_path):
        rom_dir = work / "tmpROM"
        subprocess.run([*self.tool("wit"), "extract", iso_path, f"{rom_dir}/"], check=True)
        
        folders = [item for item in rom_dir.iterdir() if item.is_dir()]
        folder_name = folders[0]
        folder_path = rom_dir / folder_name.name / "sys" / "main.dol"
        folder_path_raw = rom_dir / folder_name.name
        dol_dir = work / "tmpDOL"

        subprocess.run([*self.tool("GeckoLoader"), "--hooktype=GX", "--optimize", str(folder_path), str(codes_path), "--dest=" + str(dol_dir)], check=True)
        
        folder_path.unlink()
        shutil.move(str(dol_dir / "main.dol"), str(folder_path))
        
        output = work / "game.wbfs"
        subprocess.run([*self.tool("wit"), "copy", str(folder_path_raw), "--dest=" + str(output)], check=True)
        
        # Request save file dialog from main thread
        self.save_file_requested.emit(".wbfs", gameName[:-4] + " (Modded).wbfs", "WBFS Files (*.wbfs)")
        # Wait for the result
        while self.save_file_path is None:
            self.msleep(100)
        
        if self.save_file_path:
            shutil.move(str(output), self.save_file_path)

    def handle_n64_rom(self, iso_path, gameName, work, codes_path):
        identity = inspect_n64(iso_path)
        targets = code_targets(self.codes_text)
        if len(targets) == 1:
            valid, message = validate_code_target(self.codes_text, next(iter(targets)))
            if not valid:
                raise ValueError(message)
            if identity.pp64_game and identity.pp64_game != next(iter(targets)):
                raise ValueError(
                    f"ROM hash identifies {identity.pp64_game.upper()}, but the codes target "
                    f"{next(iter(targets)).upper()}."
                )
        output = work / "game.z64"
        subprocess.run([*self.tool("GSInject"), str(codes_path), iso_path, str(output)], check=True)
        
        # Request save file dialog from main thread
        self.save_file_requested.emit(".z64", gameName[:-4] + " (Modded).z64", "Z64 Files (*.z64)")
        # Wait for the result
        while self.save_file_path is None:
            self.msleep(100)
        
        if self.save_file_path:
            shutil.move(str(output), self.save_file_path)

    def handle_regular_iso(self, iso_path, gameName, work, codes_path):
        rom_dir = work / "tmpROM"
        subprocess.run([*self.tool("wit"), "extract", iso_path, f"{rom_dir}/"], check=True)
        
        folders = [item for item in rom_dir.iterdir() if item.is_dir()]
        folder_name = folders[0]
        folder_path = rom_dir / folder_name.name / "sys" / "main.dol"
        folder_path_raw = rom_dir / folder_name.name
        dol_dir = work / "tmpDOL"
        
        subprocess.run([*self.tool("GeckoLoader"), "--hooktype=GX", str(folder_path), str(codes_path), "--dest=" + str(dol_dir)], check=True)
        
        folder_path.unlink()
        shutil.move(str(dol_dir / "main.dol"), str(folder_path))
        
        output = work / "game.iso"
        subprocess.run([*self.tool("wit"), "copy", str(folder_path_raw), "--dest=" + str(output)], check=True)
        
        # Request save file dialog from main thread
        self.save_file_requested.emit(".iso", gameName[:-4] + " (Modded).iso", "ISO Files (*.iso)")
        # Wait for the result
        while self.save_file_path is None:
            self.msleep(100)
        
        if self.save_file_path:
            shutil.move(str(output), self.save_file_path)


class InjectorPage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file_path = ""
        self.setup_ui()

    def setup_ui(self):
        """Set up the injector page UI"""
        self.setObjectName("injectorPage")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = SubtitleLabel("Code Injector")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Description
        desc = BodyLabel("Inject generated codes into your Mario Party games")
        desc.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc)
        
        # File selection card
        file_card = CardWidget()
        file_layout = QVBoxLayout(file_card)
        file_layout.setSpacing(12)
        
        file_title = BodyLabel("Select ROM/ISO File")
        file_layout.addWidget(file_title)
        
        # File selection row
        file_row = QHBoxLayout()
        self.file_path_edit = LineEdit()
        self.file_path_edit.setPlaceholderText("No file selected")
        self.file_path_edit.setReadOnly(True)
        file_row.addWidget(self.file_path_edit)
        
        self.select_file_btn = PushButton("Browse")
        self.select_file_btn.clicked.connect(self.select_file)
        file_row.addWidget(self.select_file_btn)
        
        file_layout.addLayout(file_row)
        main_layout.addWidget(file_card)
        
        # Codes input card
        codes_card = CardWidget()
        codes_layout = QVBoxLayout(codes_card)
        codes_layout.setSpacing(12)
        
        codes_title = BodyLabel("Enter Codes")
        codes_layout.addWidget(codes_title)
        
        codes_desc = BodyLabel("Paste your generated codes here (one per line)")
        codes_layout.addWidget(codes_desc)
        
        self.codes_text_edit = TextEdit()
        self.codes_text_edit.setPlaceholderText("Paste your codes here...")
        self.codes_text_edit.setMaximumHeight(200)
        self.codes_text_edit.setStyleSheet("TextEdit { color: palette(text); }")
        self.codes_text_edit.textChanged.connect(self.on_codes_changed)
        codes_layout.addWidget(self.codes_text_edit)
        
        main_layout.addWidget(codes_card)
        
        # Inject button
        self.inject_btn = PushButton("Inject Codes")
        self.inject_btn.clicked.connect(self.inject_codes)
        self.inject_btn.setEnabled(False)
        main_layout.addWidget(self.inject_btn)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
    
    def select_file(self):
        """Open file dialog to select ROM/ISO file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ROM/ISO File",
            "",
            "Game Files (*.z64 *.iso *.wbfs);;Z64 Files (*.z64);;ISO Files (*.iso);;WBFS Files (*.wbfs);;All Files (*.*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            self.file_path_edit.setText(file_path)
            self.update_inject_button_state()
    
    def on_codes_changed(self):
        """Handle text changes in codes text edit"""
        self.update_inject_button_state()
    
    def update_inject_button_state(self):
        """Update the inject button enabled state based on file selection and codes"""
        has_file = bool(self.selected_file_path)
        has_codes = bool(self.codes_text_edit.toPlainText().strip())
        self.inject_btn.setEnabled(has_file and has_codes)
    
    def inject_codes(self):
        """Start the code injection process"""
        if not self.selected_file_path:
            createDialog("Error", "error", "Please select a ROM/ISO file first.", None)
            return
        
        codes_text = self.codes_text_edit.toPlainText().strip()
        if not codes_text:
            createDialog("Error", "error", "Please enter codes to inject.", None)
            return
        
        if not os.path.exists(self.selected_file_path):
            createDialog("Error", "error", "Selected file does not exist.", None)
            return
        
        # Disable button during injection
        self.inject_btn.setEnabled(False)
        self.inject_btn.setText("Injecting...")
        
        # Start injection worker thread
        self.injection_worker = InjectionWorker(self.selected_file_path, codes_text, self)
        self.injection_worker.finished.connect(self.on_injection_finished)
        self.injection_worker.save_file_requested.connect(self.handle_save_file_request)
        self.injection_worker.start()
    
    def handle_save_file_request(self, extension, initial_name, file_types):
        """Handle save file request from worker thread"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Modified Game File",
            initial_name,
            f"{file_types};;All Files (*.*)"
        )
        
        # Set the result back to the worker thread
        if file_path:
            self.injection_worker.save_file_path = file_path
        else:
            self.injection_worker.save_file_path = ""  # User cancelled
    
    def on_injection_finished(self, success, message):
        """Handle injection completion"""
        # Re-enable button
        self.inject_btn.setEnabled(True)
        self.inject_btn.setText("Inject Codes")
        
        if success:
            createDialog("Success", "success", message, None)
        else:
            createDialog("Error", "error", message, None)
