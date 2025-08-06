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
from datetime import datetime
from PyQt6.QtWidgets import QListWidget
from mtbp3cd.util.lsr import LsrTree

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, 
    QPushButton, QLabel,
    QTableWidget, QFileDialog,
    QTabWidget, QHBoxLayout,
    QTableWidgetItem
)

class TabFolder(QWidget):
    def __init__(self, _p):
        super().__init__()
        layout_tab_folder = QVBoxLayout()
        layout_tab_folder.setAlignment(Qt.AlignmentFlag.AlignTop)

        # BOX - Save button
        layout_button = QHBoxLayout()

        self.select_button = QPushButton("Step 1: Select")
        self.select_button.setEnabled(True)
        self.select_button.clicked.connect(self.select_button_f)
        layout_button.addWidget(self.select_button)

        self.list_tree_button = QPushButton("Step 2: Save tree and list")
        self.list_tree_button.setEnabled(False)
        self.list_tree_button.clicked.connect(lambda: self.list_tree_button_f(_p))
        layout_button.addWidget(self.list_tree_button)

        # BOX - Export DataFrame as CSV
        self.list_table_button = QPushButton("Step 3: Save table")
        self.list_table_button.setEnabled(False)
        self.list_table_button.clicked.connect(lambda: self.list_table_button_f(_p))
        layout_button.addWidget(self.list_table_button)
        layout_tab_folder.addLayout(layout_button)

        # BOX - tabs
        self.tabs = QTabWidget()
        self.tab_meta = QWidget()
        self.tab_tree = QWidget()
        self.tab_table = QWidget()
        self.tab_list = QWidget()

        # BOX - Tab Meta 
        layout_tab_meta = QVBoxLayout()
        layout_tab_meta.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.meta_info = QLabel("Info: None")
        self.meta_info.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.meta_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.meta_info.setStyleSheet("font-family: 'Courier New', monospace; border: 1px groove #cccccc; border-radius: 4px; padding: 4px 8px;")
        layout_tab_meta.addWidget(self.meta_info)
        self.tab_meta.setLayout(layout_tab_meta)

        # BOX - Tab Tree 
        layout_tab_tree = QVBoxLayout()
        layout_tab_tree.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tab_tree_str = QListWidget()
        self.tab_tree_str.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.tab_tree_str.setStyleSheet("font-family: 'Courier New', monospace;")
        layout_tab_tree.addWidget(self.tab_tree_str)
        self.tab_tree.setLayout(layout_tab_tree)

        # BOX - DataFrame Preview 
        layout_tab_table = QVBoxLayout()
        layout_tab_table.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tab_table_qttable = QTableWidget()
        self.tab_table_qttable.setColumnCount(0)
        self.tab_table_qttable.setRowCount(0)
        self.tab_table_qttable.setVisible(True)
        layout_tab_table.addWidget(self.tab_table_qttable)
        self.tab_table.setLayout(layout_tab_table)

        # BOX - Tab List 
        layout_tab_list = QVBoxLayout()
        layout_tab_list.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tab_list_str = QListWidget()
        self.tab_list_str.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.tab_list_str.setStyleSheet("font-family: 'Courier New', monospace;")
        layout_tab_list.addWidget(self.tab_list_str)
        self.tab_list.setLayout(layout_tab_list)

        ###### TAB - ALL ######
        self.tabs.addTab(self.tab_meta, "Meta")
        self.tabs.addTab(self.tab_tree, "Tree")
        self.tabs.addTab(self.tab_table, "Table")
        self.tabs.addTab(self.tab_list, "List")

        layout_tab_folder.addWidget(self.tabs)

        # BOX - Message List Widget
        self.message_list = QListWidget()
        self.message_list.setFixedHeight(self.message_list.sizeHintForRow(0) + 40)
        self.message_list.setStyleSheet("background-color: rgba(211, 211, 211, 0.15);")
        layout_tab_folder.addWidget(self.message_list)

        self.setLayout(layout_tab_folder)

    def show_message(self, message, success=True):
        color = "#528B55" if success else "#B55555"
        self.message_list.addItem(message)
        self.message_list.item(self.message_list.count() - 1).setForeground(Qt.GlobalColor.green if success else Qt.GlobalColor.red)
        self.message_list.scrollToBottom()

    def select_button_f(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.tab_folder_meta_str = self.util_get_folder_meta_info(folder)
            self.tab_folder_path = folder
            self.meta_info.setText(self.tab_folder_meta_str)
            lsr1 = LsrTree(folder, outfmt="tree", with_counts=True)
            self.tab_folder_tree_str = lsr1.list_files() 
            self.list_tree_button.setEnabled(bool(len(self.tab_folder_tree_str)>0))
            self.tab_tree_str.clear()
            self.tab_tree_str.addItems([str(item) for item in self.tab_folder_tree_str])
            #self.tab_tree_str.setText( self.tab_folder_tree_str )
            lsr2 = LsrTree(folder, outfmt="dataframe")
            self.folder_file_list = lsr2.list_files_list()
            self.folder_file_df = lsr2.list_files_dataframe()
            self.list_table_button.setEnabled(self.folder_file_df is not None)
            self.tab_list_str.clear()
            self.tab_list_str.addItems([str(item) for item in self.folder_file_list])

            # Display DataFrame in the QTableWidget
            self.tab_table_qttable.clear()
            self.tab_table_qttable.setRowCount(self.folder_file_df.shape[0])
            self.tab_table_qttable.setColumnCount(self.folder_file_df.shape[1])
            self.tab_table_qttable.setHorizontalHeaderLabels([str(col) for col in self.folder_file_df.columns])

            for row in range(self.folder_file_df.shape[0]):
                for col in range(self.folder_file_df.shape[1]):
                    value = str(self.folder_file_df.iat[row, col])
                    item = QTableWidgetItem(value)
                    self.tab_table_qttable.setItem(row, col, item)
            self.tab_table_qttable.resizeColumnsToContents()

    @staticmethod
    def util_get_folder_meta_info(folder):
        folder_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, _, filenames in os.walk(folder)
            for filename in filenames
        )
        folder_ctime = datetime.fromtimestamp(os.path.getctime(folder))
        folder_mtime = datetime.fromtimestamp(os.path.getmtime(folder))
        now = datetime.now()
        return (
            f"Folder path: {folder}\n"
            f"Folder size: {folder_size:,} bytes\n"
            f"Created: {folder_ctime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Modified: {folder_mtime.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Scan time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"User: {os.getlogin()}"
        )

    def list_tree_button_f(self, _p):
        file_path_base = getattr(_p.tab_starting, "output_folder_path", None)
        if not file_path_base:
            self.show_message("Please select output folder in the previous step", success=False)
            return
        file_path = os.path.join(file_path_base, "folder_list_tree.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.tab_folder_meta_str + "\n\n")
                for item in self.tab_folder_tree_str:
                    f.write(str(item) + "\n")
                for item in self.folder_file_list:
                    f.write(str(item) + "\n")
            self.show_message(f"Tree exported: {file_path}", success=True)
        except Exception as e:
            self.show_message(f"Failed to export: {e}", success=False)

    def list_table_button_f(self, _p):
        file_path_base = getattr(_p.tab_starting, "output_folder_path", None)
        if not file_path_base:
            self.show_message("Please select output folder in the previous step", success=False)
            return
        file_path = os.path.join(file_path_base, "folder_list_table.csv")
        try:
            self.folder_file_df.to_csv(file_path, index=False)
            self.show_message(f"CSV exported: {file_path}", success=True)
        except Exception as e:
            self.show_message(f"Failed to export CSV: {e}", success=False)


if __name__ == "__main__":
    pass