from PySide6.QtWidgets import (QMainWindow,QMessageBox, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QProgressBar, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                               QCheckBox, QFileDialog, QBoxLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from scanner_func import Scanner

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.scanner = Scanner()
        self.setWindowTitle("Directory Scanner")

        self.directory_to_scan = None
        self.config_file = None

        self.files_scanned = 0
        self.problems_found = 0
        self.issues_solved = 0

        self.result_label = None
        self.issues_solved_label = None

        self.table = None
        self.row_selected = None

        self.rename_btn = None
        self.move_btn = None
        self.ignore_btn = None
        self.delete_btn = None
        self.explorer_btn = None

        self.issues = []

        self.draw_interface()
        self.restore_ui()


    def draw_interface(self):
        main_container = QWidget()
        main_container.resize(600, 500)
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)

        # to scan row
        to_scan_row = QHBoxLayout()

        label_to_scan = QLabel("Directory to scan")
        label_to_scan.setFixedWidth(100)
        self.directory_to_scan = QLineEdit()
        self.directory_to_scan.setFixedWidth(500)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.pick_scan_directory)

        to_scan_row.addWidget(label_to_scan)
        to_scan_row.addWidget(self.directory_to_scan)
        to_scan_row.addWidget(browse_button)

        main_layout.addLayout(to_scan_row)

        # config row
        config_row = QHBoxLayout()

        label_config = QLabel("Config file")
        label_config.setFixedWidth(100)
        self.config_file = QLineEdit()
        self.config_file.setFixedWidth(500)
        browse_button_config = QPushButton("Browse")
        browse_button_config.clicked.connect(self.pick_config_file)
        reload_btn = QPushButton()
        reload_btn.setIcon(QIcon("reload_icon.png"))
        reload_btn.setFixedWidth(50)
        reload_btn.clicked.connect(self.reload_config)

        config_row.addWidget(label_config)
        config_row.addWidget(self.config_file)
        config_row.addWidget(browse_button_config)
        config_row.addWidget(reload_btn)
        main_layout.addLayout(config_row)

        # scan button
        scan_btn = QPushButton("Scan")
        scan_btn.clicked.connect(self.scan_executed)
        main_layout.addWidget(scan_btn)

        # progress bar
        # self.progress_bar = QProgressBar()
        # self.progress_bar.setMinimum(0)
        # self.scanner.scan_started.connect(self.progress_bar.setMaximum)
        # self.scanner.progress_updated.connect(self.progress_bar.setValue)
        # self.progress_bar.hide()
        # main_layout.addWidget(self.progress_bar)

        # separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # result row
        result_row = QHBoxLayout()
        result_row.setSpacing(0)
        result_row.setContentsMargins(0,0,0,0)
        self.result_label = QLabel(f"Result: {self.files_scanned} files scanned - {self.problems_found} issues found - {self.issues_solved} issues solved")
        self.result_label.setAlignment(Qt.AlignLeft)
        result_row.addWidget(self.result_label)
        self.issues_solved_label = QLabel(f" - {self.issues_solved} issues solved")
        self.issues_solved_label.setAlignment(Qt.AlignLeft)
        result_row.addWidget(self.issues_solved_label)
        main_layout.addLayout(result_row)

        # table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["File", "Issue", "Info"])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 300)
        self.table.horizontalHeader().setStretchLastSection(True)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_row_selected)

        main_layout.addWidget(self.table)

        # bottom btns
        btns_row = QHBoxLayout()
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.clicked.connect(self.rename_selected)
        self.rename_btn.setEnabled(False) ##439e42
        self.rename_btn.setStyleSheet("""
            QPushButton:enabled {
                background-color: #4f694e;
                color: white;
            }
        """)

        self.move_btn = QPushButton("Move")
        self.move_btn.clicked.connect(self.move_selected)
        self.move_btn.setEnabled(False)
        self.move_btn.setStyleSheet("""
            QPushButton:enabled {
                background-color: #4f694e;
                color: white;
            }
        """)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setStyleSheet("background-color: #9e4442; color: white;")

        self.ignore_btn = QPushButton("Ignore")
        self.ignore_btn.clicked.connect(self.ignore_file)
        self.ignore_btn.setStyleSheet("background-color: #9e7942; color: white;")

        self.explorer_btn = QPushButton("Open in Explorer")
        self.explorer_btn.clicked.connect(self.explorer_selected)

        btns_row.addWidget(self.rename_btn)
        btns_row.addWidget(self.move_btn)
        btns_row.addWidget(self.delete_btn)
        btns_row.addWidget(self.ignore_btn)
        btns_row.addWidget(self.explorer_btn)

        main_layout.addLayout(btns_row)

    def insert_issue_row(self, filename, issue, info):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(filename))
        self.table.setItem(row, 1, QTableWidgetItem(issue))
        self.table.setItem(row, 2, QTableWidgetItem(info))

    def pick_scan_directory(self):
        scan_directory = QFileDialog().getExistingDirectory()
        self.directory_to_scan.setText(scan_directory)

    def pick_config_file(self):
        config_file = QFileDialog().getOpenFileName()
        self.config_file.setText(config_file[0])
        self.scanner.load_config(config_file[0])

    def reload_config(self):
        error = self.scanner.load_config(self.config_file.text())
        if error:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error loading config")
            msg.setText(error)
            msg.exec()

    def scan_executed(self):
        # resetting from previous scan
        self.table.setRowCount(0)
        self.issues.clear()
        self.issues_solved = 0

        nr_files, result = self.scanner.scan(self.directory_to_scan.text())
        self.files_scanned = nr_files
        self.problems_found = len(result)
        self.reload_result_row()

        if type(result) == str:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error scanning directory")
            msg.setText(result)
            msg.exec()
        else:
            self.issues = result
            for issue in result:
                self.insert_issue_row(issue.filename, issue.issue, issue.info)

    def reload_result_row(self):
        self.result_label.setText(
            f"Result: {self.files_scanned} files scanned - {self.problems_found} issues found - {self.issues_solved} issues solved"
        )

    def on_row_selected(self):
        selected_rows = self.table.selectedItems()

        if not selected_rows:
            return

        row = self.table.currentRow()
        self.row_selected = self.issues[row]
        self.update_btns()

    def update_btns(self):
        selected_rows = self.table.selectionModel().selectedRows()

        if len(selected_rows) == 0:
            self.rename_btn.setEnabled(False)
            self.move_btn.setEnabled(False)

        selected_issues = []
        for selected_row in selected_rows:
            row_nr = selected_row.row()
            issue = self.table.item(row_nr, 1).text()
            selected_issues.append(issue)

        if all(issue == "File format" for issue in selected_issues):
            self.rename_btn.setEnabled(False)
            self.move_btn.setEnabled(False)
        elif all(issue == "Folder location" for issue in selected_issues):
            self.rename_btn.setEnabled(False)
            self.move_btn.setEnabled(True)
        elif all(issue == "Prefix" or issue == "Suffix" for issue in selected_issues):
            self.rename_btn.setEnabled(True)
            self.move_btn.setEnabled(False)
        elif all(issue == "Image size" for issue in selected_issues):
            self.rename_btn.setEnabled(False)
            self.move_btn.setEnabled(False)
        else:
            self.rename_btn.setEnabled(False)
            self.move_btn.setEnabled(False)

    def ignore_file(self):
        if self.row_selected is None:
            return

        rows = self.table.selectionModel().selectedRows()
        for row in rows:
            row_nr = row.row()
            self.table.removeRow(row_nr)
            self.issues.pop(row_nr)
            self.row_selected = None

    def rename_selected(self):
        success = self.scanner.rename_file(self.row_selected)
        if success:
            self.remove_row_on_success()

    def move_selected(self):
        succes = self.scanner.move_file(self.row_selected, self.directory_to_scan.text())
        if succes:
            self.remove_row_on_success()

    def remove_row_on_success(self):
        row = self.table.currentRow()
        self.table.removeRow(row)
        self.issues.pop(row)
        self.row_selected = None
        self.issues_solved_update()
        self.update_btns()

    def delete_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        files = []
        for row in selected_rows:
            row_nr = row.row()
            issue_filepath = self.issues[row_nr].filepath
            files.append(issue_filepath)

        self.scanner.delete_files(files)

    def explorer_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        files = []
        for row in selected_rows:
            row_nr = row.row()
            issue_filepath = self.issues[row_nr].filepath
            files.append(issue_filepath)

        self.scanner.open_in_explorer(files)

    def issues_solved_update(self):
        self.issues_solved += 1
        self.reload_result_row()

    def restore_ui(self):
        state = self.scanner.load_ui()

        if not state:
            return

        self.directory_to_scan.setText(state["directory"])
        self.config_file.setText(state["config_path"])
        self.scanner.load_config(state["config_path"])
        self.issues = state["issues"]

        for issue in state["issues"]:
            self.insert_issue_row(issue.filename, issue.issue, issue.info)

    def closeEvent(self, event):
        self.scanner.save_ui(
            self.directory_to_scan.text(),
            self.config_file.text(),
            self.issues
        )
        event.accept()