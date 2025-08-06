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


"""
This module provides the main GUI components for the File Inventory Tool application.

Classes:
    MainWedge (QWidget): The main widget containing the sidebar and tabbed interface for navigating
        between different sections of the application, including output folder selection, input folder
        selection, and checksum viewing.
    FileInventoryApp (QMainWindow): The main window of the application, setting up the main widget
        and window properties.

The GUI is built using PyQt6 and organizes the workflow into three main tabs, accessible via a sidebar:
    - "Select Output Folder": For selecting and viewing the output folder.
    - "Select Input Folder": For selecting and viewing the input folder.
    - "Checksums": For viewing file checksums.

The sidebar buttons update the visible tab and highlight the selected section for user navigation.

Dependencies:
    - PyQt6
    - pandas

Usage:
    Run this module as the main program to launch the File Inventory Tool GUI.

"""
import os
import pandas as pd
import sys
from PyQt6.QtCore import Qt

from datetime import datetime
import mtbp3cd.gui.gt01r_starting as gt01r_starting, mtbp3cd.gui.gt01r_inputfolder as gt01r_inputfolder, mtbp3cd.gui.gt01o_tabchecksum as gt01o_tabchecksum 

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QLabel,
)

class MainWedge(QWidget):
    def __init__(self):
        super().__init__()
        self.style_btn_clicked = "QPushButton { background-color: #0078d7; color: white; border: none; padding: 3px 16px; border-radius: 4px; }"

        self.tabs = QTabWidget()
        self.tabs.tabBar().setVisible(False)
        self.tab_starting = gt01r_starting.TabStarting()
        self.tab_folder = gt01r_inputfolder.TabFolder(self)
        self.tab_checksum = gt01o_tabchecksum.TabChecksum(self)

        ###### TAB - starting ######
        layout_tab_starting = QVBoxLayout()
        layout_tab_starting.setAlignment(Qt.AlignmentFlag.AlignTop)

        ###### TAB - ALL ######
        self.tabs.addTab(self.tab_starting, "View Output Folder")
        self.tabs.addTab(self.tab_folder, "View Input Folder")
        self.tabs.addTab(self.tab_checksum, "View Checksums")

        ###### SIDEBAR ######
        self.sidebar_button_starting = QPushButton("Select Output Folder")
        self.sidebar_button_starting.setChecked(True)
        self.sidebar_button_starting.setStyleSheet(self.style_btn_clicked)
        self.sidebar_button_folder = QPushButton("Select Input Folder")
        self.sidebar_button_checksum = QPushButton("Checksums")

        self.sidebar_button_starting.clicked.connect(self.sidebar_button_starting_f)
        self.sidebar_button_folder.clicked.connect(self.sidebar_button_folder_f)
        self.sidebar_button_checksum.clicked.connect(self.sidebar_button_checksum_f)

        self.sidebar_button_starting.setCheckable(True)
        self.sidebar_button_folder.setCheckable(True)
        self.sidebar_button_checksum.setCheckable(True)

        # Sidebar layout
        layout_sidebar = QVBoxLayout()
        layout_sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_sidebar.addWidget(QLabel("<b>Starts Here:</b>"))
        layout_sidebar.addWidget(self.sidebar_button_starting)
        layout_sidebar.addWidget(self.sidebar_button_folder)
        layout_sidebar.addWidget(self.sidebar_button_checksum)
        layout_sidebar.addWidget(QLabel("<b>Task:</b>"))

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(layout_sidebar)

        # Main Layout
        layout_h = QHBoxLayout()
        layout_h.addWidget(sidebar_widget)
        layout_h.addWidget(self.tabs)
        self.setLayout(layout_h)

    def update_sidebar_buttons_f(self, clicked_button):
        for btn in [
            self.sidebar_button_starting,
            self.sidebar_button_folder,
            self.sidebar_button_checksum,
        ]:
            if btn is clicked_button:
                btn.setStyleSheet(self.style_btn_clicked)
                btn.setChecked(True)
            else:
                btn.setStyleSheet("")
                btn.setChecked(False)

    def sidebar_button_starting_f(self):
        self.tabs.setCurrentWidget(self.tab_starting)
        self.update_sidebar_buttons_f(self.sidebar_button_starting)

    def sidebar_button_folder_f(self):
        self.tabs.setCurrentWidget(self.tab_folder)
        self.update_sidebar_buttons_f(self.sidebar_button_folder)

    def sidebar_button_checksum_f(self):
        self.tabs.setCurrentWidget(self.tab_checksum)
        self.update_sidebar_buttons_f(self.sidebar_button_checksum)


class FileInventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Inventory Tool")
        self.setGeometry(100, 100, 800, 600)
        self.main_widget = MainWedge()
        self.setCentralWidget(self.main_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileInventoryApp()
    window.show()
    sys.exit(app.exec())
