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
from mtbp3cd.util.lsr import LsrTree
from datetime import datetime
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator 
import json

from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout,
    QTabWidget, QTextEdit,
    QWidget, QVBoxLayout, 
    QListWidget,
    QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog
)

class TabRecord(QWidget):
    def __init__(self, _p):
        super().__init__()
        self._p = _p

        self.tab_button_1 = QPushButton("Select Record[R] Folder")
        self.tab_button_1.clicked.connect(self.tab_button_1_f)
        self.tab_button_2 = QPushButton("Save Diff table.csv")
        self.tab_button_2.clicked.connect(self.tab_button_2_f)

        layout_tab_button = QHBoxLayout()
        layout_tab_button.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab_button.addWidget(self.tab_button_1)
        layout_tab_button.addWidget(self.tab_button_2)

        self.tab_tabs_table_1 = QTableWidget()
        self.tab_tabs_table_1.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_tabs_table_2 = QTableWidget()
        self.tab_tabs_table_2.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_tabs_table_3 = QTableWidget()
        self.tab_tabs_table_3.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.tab_tabs = QTabWidget()
        self.tab_tabs.tabBar().setVisible(True)
        self.tab_tabs.addTab(self.tab_tabs_table_1, "Diff Meta [R] vs. [I]")
        self.tab_tabs.addTab(self.tab_tabs_table_2, "Table [R]")
        self.tab_tabs.addTab(self.tab_tabs_table_3, "Diff Table [I] vs. [R]")

        self.message_list = QListWidget()
        self.message_list.setFixedHeight(self.message_list.sizeHintForRow(0) + 70)
        self.message_list.setStyleSheet("background-color: rgba(80, 80, 80, 0.15);")

        layout_tab = QVBoxLayout()
        layout_tab.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_tab.addLayout(layout_tab_button)
        layout_tab.addWidget(self.tab_tabs)
        layout_tab.addWidget(self.message_list)
        self.setLayout(layout_tab)

    def tab_button_1_f(self):
        start_dir = os.path.expanduser("~")
        if not hasattr(self._p, "tab_folder"):
            self.show_message("Input folder tab not set.", success=False)
            return
        if not hasattr(self._p.tab_folder, "gt01_input_folder_path") or not self._p.tab_folder.gt01_input_folder_path:
            self.show_message("Input folder path not set.", success=False)
            if not hasattr(self._p.tab_starting, "gt01_output_folder_path") or not self._p.tab_starting.gt01_output_folder_path:
                self.show_message("Output folder path not set.", success=False)
                return
            start_dir = self._p.tab_starting.gt01_output_folder_path 
            output_meta_path = os.path.join(self._p.tab_starting.gt01_output_folder_path, "log_folder_meta.json")
            if os.path.exists(output_meta_path):
                self.show_message("Try finding log files in output folder as the recent snapshot.", success=True)
                try:
                    with open(output_meta_path, "r", encoding="utf-8") as f:
                        self.input_meta_json = json.load(f)
                    self.show_message(f"Loaded input meta: {output_meta_path}", success=True)
                except Exception as e:
                    self.input_meta_json = None
                    self.show_message(f"Failed to read input meta.json: {e}", success=False)
            else:
                self.input_meta_json = None
                self.show_message("log_folder_meta.json not found in output folder.", success=False)
            # Try to read log_folder_table.csv from output folder
            table_path = os.path.join(self._p.tab_starting.gt01_output_folder_path, "log_folder_table.csv")
            if os.path.exists(table_path):
                try:
                    self.input_table_df = pd.read_csv(table_path)
                    self.show_message(f"Loaded table: {table_path}", success=True)
                except Exception as e:
                    self.input_meta_json = pd.DataFrame()
                    self.show_message(f"Failed to read table.csv: {e}", success=False)
            else:
                self.input_meta_json = pd.DataFrame()
                self.show_message("log_folder_table.csv not found in output folder.", success=False)
        else:
            start_dir = self._p.tab_folder.gt01_input_folder_path 
            if not getattr(self._p.tab_folder, "tab_folder_meta_json", None):
                self.show_message("Input folder meta not found.", success=False)
                return
            if not isinstance(self._p.tab_folder.tab_folder_meta_json, dict):
                self.show_message("Input folder meta is not a dict.", success=False)
                return
            self.input_meta_json = self._p.tab_folder.tab_folder_meta_json
            if hasattr(self._p.tab_folder, "folder_file_df") and isinstance(self._p.tab_folder.folder_file_df, pd.DataFrame):
                self.input_table_df = self._p.tab_folder.folder_file_df
            else:
                self.input_table_df = pd.DataFrame()
            
        folder = QFileDialog.getExistingDirectory(self, "Select Record Folder", start_dir)
        if folder:
            self.show_message(f"Selected folder: {folder}", success=True)
            log_files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and f.startswith("log_folder_")]
            if log_files:
                self.show_message(f"Found log files: {', '.join(log_files)}", success=True)
                table_path = os.path.join(folder, "log_folder_table.csv")
                if os.path.exists(table_path):
                    try:
                        df = pd.read_csv(table_path)
                        if "md5" in df.columns:
                            df = df.drop(columns=["md5"])
                        self.show_message(f"Loaded table: {table_path}", success=True)
                        self.tab_tabs_table_2.clear()
                        self.tab_tabs_table_2.setRowCount(len(df))
                        self.tab_tabs_table_2.setColumnCount(len(df.columns))
                        self.tab_tabs_table_2.setHorizontalHeaderLabels(df.columns.astype(str).tolist())
                        for row in range(len(df)):
                            for col in range(len(df.columns)-1):
                                value = str(df.iat[row, col])
                                self.tab_tabs_table_2.setItem(row, col, QTableWidgetItem(value))
                        self.tab_tabs_table_2.resizeColumnsToContents()

                        # Compare df (record) and self._p.tab_folder.folder_file_df (input)
                        if not self.input_table_df.empty:
                            common_cols = [col for col in df.columns if col in self.input_table_df.columns]
                            if not common_cols:
                                self.show_message("No common columns to compare.", success=False)
                            else:
                                # Merge on common columns (assume first column is a key if exists)
                                if "size_in_bytes" in df.columns:
                                    df["size_in_bytes"] = pd.to_numeric(df["size_in_bytes"], errors="coerce").astype("Int64")
                                if "size_in_bytes" in self.input_table_df.columns:
                                    self.input_table_df["size_in_bytes"] = pd.to_numeric(self.input_table_df["size_in_bytes"], errors="coerce").astype("Int64")
                                if "N_page" in df.columns:
                                    df["N_page"] = pd.to_numeric(df["N_page"], errors="coerce").astype("Int64")
                                if "N_page" in self.input_table_df.columns:
                                    self.input_table_df["N_page"] = pd.to_numeric(self.input_table_df["N_page"], errors="coerce").astype("Int64")
                                if "N_column" in df.columns:
                                    df["N_column"] = pd.to_numeric(df["N_column"], errors="coerce").astype("Int64")
                                if "N_column" in self.input_table_df.columns:
                                    self.input_table_df["N_column"] = pd.to_numeric(self.input_table_df["N_column"], errors="coerce").astype("Int64")
                                if "N_row" in df.columns:
                                    df["N_row"] = pd.to_numeric(df["N_row"], errors="coerce").astype("Int64")
                                if "N_row" in self.input_table_df.columns:
                                    self.input_table_df["N_row"] = pd.to_numeric(self.input_table_df["N_row"], errors="coerce").astype("Int64")
                                self.merged = pd.merge(
                                    self.input_table_df, df, 
                                    on=common_cols,
                                    how="outer", 
                                    suffixes=("_I", "_R"), 
                                    indicator=True
                                )
                                if "md5" in self.merged.columns:
                                    self.merged = self.merged.drop(columns=["md5"])

                                both_count = (self.merged["_merge"] == "both").sum()
                                left_only_count = (self.merged["_merge"] == "left_only").sum()
                                right_only_count = (self.merged["_merge"] == "right_only").sum()
                                total_count = both_count + left_only_count + right_only_count
                                self.show_message(
                                    f"Diff summary: both={both_count}, input_only={left_only_count}, record_only={right_only_count}, total={total_count}",
                                    success=True
                                )
                                self.merged = self.merged[self.merged["_merge"] != "both"]
                                # Prepare diff table: show all columns from both, plus indicator
                                self.tab_tabs_table_3.clear()
                                if not both_count == total_count:
                                    self.tab_tabs_table_3.setRowCount(len(self.merged))
                                    self.tab_tabs_table_3.setColumnCount(len(self.merged.columns))
                                    self.tab_tabs_table_3.setHorizontalHeaderLabels(self.merged.columns.astype(str).tolist())
                                    for row in range(len(self.merged)):
                                        for col in range(len(self.merged.columns)):
                                            value = str(self.merged.iat[row, col])
                                            self.tab_tabs_table_3.setItem(row, col, QTableWidgetItem(value))
                                    self.tab_tabs_table_3.resizeColumnsToContents()
                        else:
                            self.show_message("Input folder_file_df not found or invalid.", success=False)
                    except Exception as e:
                        self.show_message(f"Failed to read table.csv: {e}", success=False)
                else:
                    self.show_message("log_folder_table.csv not found.", success=False)
                meta_path = os.path.join(folder, "log_folder_meta.json")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            meta_data = json.load(f)
                        self.show_message(f"Loaded meta: {meta_path}", success=True)
                        self.tab_tabs_table_1.clear()
                        if isinstance(meta_data, dict):
                            keys = list(meta_data.keys())
                            self.tab_tabs_table_1.setRowCount(len(keys))
                            self.tab_tabs_table_1.setColumnCount(6)
                            self.tab_tabs_table_1.setHorizontalHeaderLabels(["Key", "Value_in_Rec", "In_R", "In_I", "Changed", "Value_from_Input"])
                            for row, key in enumerate(keys):
                                self.tab_tabs_table_1.setItem(row, 0, QTableWidgetItem(str(key)))
                                self.tab_tabs_table_1.setItem(row, 1, QTableWidgetItem(str(meta_data[key])))
                                self.tab_tabs_table_1.setItem(row, 2, QTableWidgetItem("Y"))
                                if key in self.input_meta_json:
                                    self.tab_tabs_table_1.setItem(row, 3, QTableWidgetItem("Y"))
                                    if meta_data[key] != self.input_meta_json[key]:
                                        self.tab_tabs_table_1.setItem(row, 4, QTableWidgetItem("Y"))
                                        self.tab_tabs_table_1.setItem(row, 5, QTableWidgetItem(self.input_meta_json[key]))
                                    else:
                                        self.tab_tabs_table_1.setItem(row, 4, QTableWidgetItem("N"))
                                        self.tab_tabs_table_1.setItem(row, 5, QTableWidgetItem(""))
                                else:
                                    self.tab_tabs_table_1.setItem(row, 3, QTableWidgetItem("N"))
                                    self.tab_tabs_table_1.setItem(row, 4, QTableWidgetItem("NA"))
                                    self.tab_tabs_table_1.setItem(row, 5, QTableWidgetItem(""))
                            extra_keys = [k for k in self.input_meta_json.keys() if k not in keys]
                            if extra_keys:
                                current_row = self.tab_tabs_table_1.rowCount()
                                self.tab_tabs_table_1.setRowCount(current_row + len(extra_keys))
                                for idx, key in enumerate(extra_keys):
                                    row = current_row + idx
                                    self.tab_tabs_table_1.setItem(row, 0, QTableWidgetItem(str(key)))
                                    self.tab_tabs_table_1.setItem(row, 1, QTableWidgetItem(""))
                                    self.tab_tabs_table_1.setItem(row, 2, QTableWidgetItem("N"))
                                    self.tab_tabs_table_1.setItem(row, 3, QTableWidgetItem("Y"))
                                    self.tab_tabs_table_1.setItem(row, 4, QTableWidgetItem("NA"))
                                    self.tab_tabs_table_1.setItem(row, 5, QTableWidgetItem(self.input_meta_json[key]))
                        else:
                            self.tab_tabs_table_1.setRowCount(1)
                            self.tab_tabs_table_1.setColumnCount(1)
                            self.tab_tabs_table_1.setHorizontalHeaderLabels(["Meta Data"])
                            self.tab_tabs_table_1.setItem(0, 0, QTableWidgetItem(str(meta_data)))
                        self.tab_tabs_table_1.resizeColumnsToContents()
                    except Exception as e:
                        self.show_message(f"Failed to read meta.json: {e}", success=False)
                else:
                    self.show_message("log_folder_meta.json not found.", success=False)

            else:
                self.show_message("No log_folder_ directories found.", success=False)
        else:
            self.show_message("No folder selected.", success=False)
    
    def tab_button_2_f(self):
        if not hasattr(self._p, "tab_starting"):
            self.show_message("Output folder path not set.", success=False)
            return
        if not hasattr(self._p.tab_starting, "gt01_output_folder_path"):
            self.show_message("Output folder path not set.", success=False)
            return
        if not self._p.tab_starting.gt01_output_folder_path:
            self.show_message("Output folder path not set.", success=False)
            return
        if not self.merged.empty:
            dt_str = datetime.now().strftime("%Y%m%dT%H%M%S")
            out_path = os.path.join(self._p.tab_starting.gt01_output_folder_path, f"log_folder_diff_table_{dt_str}.csv")
            self.merged.to_csv(out_path, index=False)
            self.show_message(f"Diff table saved to: {out_path}", success=True)
        else:
            self.show_message("No diff to save: diff table is empty.", success=True)

    def show_message(self, message, success=True):
        self.message_list.addItem(message)
        self.message_list.item(self.message_list.count() - 1).setForeground(Qt.GlobalColor.green if success else Qt.GlobalColor.red)
        self.message_list.scrollToBottom()

if __name__ == "__main__":
    pass