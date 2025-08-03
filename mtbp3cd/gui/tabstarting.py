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
from datetime import datetime
from PyQt6.QtWidgets import QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator 

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QTableWidget, QFileDialog
)

class TabStarting(QWidget):
    def __init__(self):
        super().__init__()
        layout_tab = QVBoxLayout()
        layout_tab.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.output_folder_path = None

        ###### Step 1
        layout_proj_name = QVBoxLayout()
        self.box_proj_name = QLineEdit()
        self.box_proj_name.setMaxLength(12)
        self.box_proj_name.setValidator(
            QLineEdit().validator() or 
            QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9]+"))
        )
        self.box_proj_name.setPlaceholderText("Enter up to 12 chars (A-Za-z0-9)")
        layout_proj_name.addWidget(QLabel("Step 1:\nType in a NEW output folder name (or leave blank for selecting an existing folder):"))
        layout_proj_name.addWidget(self.box_proj_name)
        layout_tab.addLayout(layout_proj_name)

        ###### Step 2
        layout_output_folder1 = QVBoxLayout()
        self.output_folder_btn = QPushButton("Select Output Path")
        self.output_folder_btn.clicked.connect(self.output_folder_btn_f)
        layout_output_folder1.addWidget(QLabel("Step 2:\nSelect output path:"))
        layout_output_folder1.addWidget(self.output_folder_btn)
        layout_tab.addLayout(layout_output_folder1)

        ###### Step 3
        layout_output_folder2 = QVBoxLayout()
        self.output_folder_label = QLabel("No folder selected")
        self.create_folder_btn = QPushButton("Create and Set Output Folder")
        self.create_folder_btn.setEnabled(False)
        self.create_folder_btn.clicked.connect(self.create_folder_btn_f)
        layout_output_folder2.addWidget(QLabel("Step 3:\nConfirm that outputs will be saved to this folder:"))
        layout_output_folder2.addWidget(self.output_folder_label)
        layout_output_folder2.addWidget(self.create_folder_btn)
        layout_tab.addLayout(layout_output_folder2)

        self.setLayout(layout_tab)

    def output_folder_btn_f(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            if self.box_proj_name.text():
                date_int = int(datetime.now().strftime("%Y%m%d"))
                folder2 = os.path.join(folder, f"{self.box_proj_name.text()}_{date_int}")
            else:
                folder2 = folder
            if os.path.exists(folder2):
                self.output_folder_label.setText(f"{folder2} (Ready!)")
                self.create_folder_btn.setEnabled(False)
            else:
                self.output_folder_label.setText(folder2)
                self.create_folder_btn.setEnabled(True)
            self.output_folder_path = folder2
        else:
            self.output_folder_label.setText("No folder selected")

    def create_folder_btn_f(self):
        folder_path = self.output_folder_path
        if folder_path:
            try:
                os.makedirs(folder_path, exist_ok=True)
                self.output_folder_label.setText(f"{folder_path} (Ready!)")
            except Exception as e:
                self.output_folder_label.setText(f"Error: {str(e)}")
                self.output_folder_path = None
        else:
            self.output_folder_label.setText("No folder selected")

if __name__ == "__main__":
    pass