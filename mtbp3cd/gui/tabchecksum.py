#  Copyright (C) 2025 Y Hsu <yh202109@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public license as published by
#  the Free software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details
#
#  You should have received a copy of the GNU General Public license
#  along with this program. If not, see <https://www.gnu.org/license/>

import os
import pandas as pd
from PyQt6.QtCore import Qt
import hashlib
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QTabWidget, QTextEdit
from PyQt6.QtWidgets import QFileDialog

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QHBoxLayout
)

class TabChecksum(QWidget):
    def __init__(self, _p):
        super().__init__()
        layout_tab_checksum = QVBoxLayout()
        layout_tab_checksum.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.selected_checksum_file = None

        # Label and ComboBox for checksum type
        layout_tab_checksum_label = QHBoxLayout()
        layout_tab_checksum_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        checksum_type_label = QLabel("Checksum Type:")
        layout_tab_checksum_label.addWidget(checksum_type_label)
        self.checksum_type = QComboBox()
        self.checksum_type.addItems(["SHA-512", "SHA-256", "MD5"])
        layout_tab_checksum_label.addWidget(self.checksum_type)
        layout_tab_checksum_label.addWidget(checksum_type_label)

        layout_tab_checksum.addLayout(layout_tab_checksum_label)

        # Export Button
        layout_tab_checksum_button = QHBoxLayout()
        layout_tab_checksum_button.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.tab_checksum2_button = QPushButton("Generate")
        self.tab_checksum2_button.clicked.connect(lambda: self.tab_checksum2_button_f(_p))
        layout_tab_checksum_button.addWidget(self.tab_checksum2_button)

        self.tab_checksum1_button = QPushButton("Select")
        self.tab_checksum1_button.clicked.connect(self.tab_checksum1_button_f)
        layout_tab_checksum_button.addWidget(self.tab_checksum1_button)

        self.tab_checksum3_button = QPushButton("Check")
        self.tab_checksum3_button.clicked.connect(lambda: self.tab_checksum3_button_f(_p))
        layout_tab_checksum_button.addWidget(self.tab_checksum3_button)

        layout_tab_checksum.addLayout(layout_tab_checksum_button)

        # Tabset to display selected file and check results
        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setVisible(False)
        self.check_results_tab = QTextEdit()
        self.check_results_tab.setReadOnly(True)
        self.tab_widget.addTab(self.check_results_tab, "Check Results")

        layout_tab_checksum.addWidget(self.tab_widget)
        self.setLayout(layout_tab_checksum)

    def tab_checksum1_button_f(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Checksum Files (*.sha512 *.sha256 *.md5 *.txt);;All Files (*)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                selected_file = selected_files[0]
                try:
                    with open(selected_file, "r", encoding="utf-8") as f:
                        lines = []
                        for i in range(10):
                            line = f.readline()
                            if not line:
                                break
                            lines.append(line.rstrip('\n'))
                    self.check_results_tab.setPlainText("\n".join(lines))
                    self.selected_checksum_file = selected_file
                except Exception as e:
                    self.check_results_tab.setPlainText(f"Error reading file: {e}")

    def tab_checksum3_button_f(self, _p):
        if not self.selected_checksum_file:
            self.check_results_tab.setPlainText("No checksum file selected. Please use 'Select' to select one.")
            return

        folder_path = getattr(_p.tab_folder, "tab_folder_path", None)
        if not folder_path or not os.path.isdir(folder_path):
            self.check_results_tab.setPlainText("No valid folder selected.")
            return

        algo = self.checksum_type.currentText()
        hash_func = {
            "SHA-512": hashlib.sha512,
            "SHA-256": hashlib.sha256,
            "MD5": hashlib.md5
        }[algo]

        # Read checksums from file
        checksums = {}
        try:
            with open(self.selected_checksum_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split(None, 1)
                    if len(parts) == 2:
                        checksum, rel_path = parts
                        checksums[rel_path.strip()] = checksum.strip()
        except Exception as e:
            self.check_results_tab.setPlainText(f"Error reading checksum file: {e}")
            return

        results = []
        for rel_path, expected_checksum in checksums.items():
            abs_path = os.path.join(folder_path, rel_path)
            if not os.path.isfile(abs_path):
                results.append(f"Missing: {rel_path}")
                continue
            try:
                with open(abs_path, "rb") as f:
                    hasher = hash_func()
                    while True:
                        data = f.read(8192)
                        if not data:
                            break
                        hasher.update(data)
                    actual_checksum = hasher.hexdigest()
                if actual_checksum.lower() == expected_checksum.lower():
                    results.append(f"OK: {rel_path}")
                else:
                    results.append(f"FAIL: {rel_path} (expected {expected_checksum}, got {actual_checksum})")
            except Exception as e:
                results.append(f"Error reading {rel_path}: {e}")

        self.check_results_tab.setPlainText("\n".join(results) if results else "No files to check.")

    def tab_checksum2_button_f(self, _p):
        folder_path = getattr(_p.tab_folder, "tab_folder_path", None)
        output_folder = getattr(_p.tab_starting, "output_folder_path", None)
        if not folder_path or not os.path.isdir(folder_path):
            self.check_results_tab.setPlainText("No valid folder selected.")
            return
        if not output_folder or not os.path.isdir(output_folder):
            self.check_results_tab.setPlainText("No valid output folder.")
            return

        algo = self.checksum_type.currentText()
        hash_func = {
            "SHA-512": hashlib.sha512,
            "SHA-256": hashlib.sha256,
            "MD5": hashlib.md5
        }.get(algo)

        results = []
        
        try:
            for root, _, files in os.walk(folder_path):
                if os.path.abspath(root).startswith(os.path.abspath(output_folder)):
                    continue
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "rb") as f:
                            hasher = hash_func()
                            while True:
                                data = f.read(8192)
                                if not data:
                                    break
                                hasher.update(data)
                            checksum = hasher.hexdigest()
                        rel_path = os.path.relpath(fpath, folder_path)
                        results.append(f"{checksum}  {rel_path}")
                    except Exception as fe:
                        results.append(f"Error reading {fname}: {str(fe)}")

            # Save to output file
            ext = {
                "SHA-512": ".sha512",
                "SHA-256": ".sha256",
                "MD5": ".md5"
            }[algo]
            out_file = os.path.join(output_folder, f"checksums{ext}")
            with open(out_file, "w") as outf:
                outf.write("\n".join(results))

            self.check_results_tab.setPlainText(f"Checksums saved to:\n{out_file}")
        except Exception as e:
            self.check_results_tab.setPlainText(f"Error: {str(e)}")

if __name__ == "__main__":
    pass