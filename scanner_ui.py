from PySide6.QtWidgets import (QMainWindow,QMessageBox, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QButtonGroup, QSpacerItem)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from scanner_func import Scanner

class MainWindow(QMainWindow):

    def __init__(self):
        """
        Initialize the main window, set up internal state variables, build the UI, and restore any previously saved
        UI state.
        """
        super().__init__()
        self.scanner = Scanner()
        self.setWindowTitle("Directory Scanner")

        self.directory_to_scan = None
        self.config_file = None

        self.btn_game_ready = None
        self.btn_source = None

        self.files_scanned = 0
        self.problems_found = 0
        self.issues_solved = 0

        self.label_scanned_files = None
        self.label_issues_found = None
        self.label_issues_solved = None

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

    def restore_ui(self):
        """
        Load and apply a previously saved UI state: restores input fields, config, issue list, and scan statistics.
        Repopulates the table.
        """
        state, files_checked, issues_found, issues_solved, game_ready, source = self.scanner.load_ui()

        if not state:
            return

        error = self.scanner.load_config(state["config_path"])
        if error:
            return

        self.directory_to_scan.setText(state["directory"])
        self.config_file.setText(state["config_path"])
        self.issues = state["issues"]
        self.btn_game_ready.setChecked(game_ready)
        self.btn_source.setChecked(source)
        self.files_scanned = files_checked
        self.problems_found = issues_found
        self.issues_solved = issues_solved
        self.reload_result_row()

        for issue in state["issues"]:
            self.insert_issue_row(issue.filename, issue.issue, issue.info)

    def draw_interface(self):
        """
        Build and lay out all UI elements: input rows, scan button, stat cards, the issue table, and the bottom action
        buttons.
        """

        main_container = QWidget()
        main_container.resize(600, 500)
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(20, 20, 20, 20)

        with open("content/styles.qss", "r") as f:
            self.setStyleSheet(f.read())

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
        reload_btn.setIcon(QIcon("content/reload_icon.png"))
        reload_btn.setFixedWidth(50)
        reload_btn.clicked.connect(self.reload_config)

        config_row.addWidget(label_config)
        config_row.addWidget(self.config_file)
        config_row.addWidget(browse_button_config)
        config_row.addWidget(reload_btn)
        main_layout.addLayout(config_row)

        separator = QSpacerItem(20, 20)
        main_layout.addItem(separator)

        self.btn_game_ready = QPushButton("Game-ready assets")
        self.btn_game_ready.setObjectName("gameReadyButton")
        self.btn_source = QPushButton("Source assets")
        self.btn_source.setObjectName("sourceButton")

        self.btn_game_ready.setCheckable(True)
        self.btn_source.setCheckable(True)

        mode_row = QHBoxLayout()
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.btn_game_ready)
        self.mode_group.addButton(self.btn_source)
        self.mode_group.setExclusive(True)

        mode_row.addWidget(self.btn_game_ready)
        mode_row.addWidget(self.btn_source)
        main_layout.addLayout(mode_row)

        separator = QSpacerItem(20, 20)
        main_layout.addItem(separator)

        # scan button
        scan_btn = QPushButton("Scan")
        scan_btn.setObjectName("scanButton")
        scan_btn.setMinimumSize(20,30)
        scan_btn.clicked.connect(self.scan_executed)
        main_layout.addWidget(scan_btn)

        separator = QSpacerItem(20, 20)
        main_layout.addItem(separator)

        # cards
        cards_layout = QHBoxLayout()

        # <editor-fold desc="Files Scanned Card">
        files_scanned = QWidget()
        files_scanned.setObjectName("scannedCard")
        card_layout = QVBoxLayout(files_scanned)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(4)

        label = QLabel("FILES SCANNED")
        label.setObjectName("scannedTitle")
        label.setAlignment(Qt.AlignCenter)
        self.label_scanned_files = QLabel(str(self.files_scanned))
        self.label_scanned_files.setAlignment(Qt.AlignCenter)
        self.label_scanned_files.setObjectName("scannedAmount")

        card_layout.addWidget(label)
        card_layout.addWidget(self.label_scanned_files)

        cards_layout.addWidget(files_scanned)
        # </editor-fold>

        # <editor-fold desc="Issues Found Card">
        files_scanned = QWidget()
        files_scanned.setObjectName("issuesCard")
        card_layout = QVBoxLayout(files_scanned)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(4)

        label = QLabel("ISSUES FOUND")
        label.setObjectName("issuesTitle")
        label.setAlignment(Qt.AlignCenter)
        self.label_issues_found = QLabel(str(self.problems_found))
        self.label_issues_found.setObjectName("issuesAmount")
        self.label_issues_found.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(label)
        card_layout.addWidget(self.label_issues_found)

        cards_layout.addWidget(files_scanned)
        # </editor-fold>

        # <editor-fold desc="Issues Solved Card">
        files_scanned = QWidget()
        files_scanned.setObjectName("solvedCard")
        card_layout = QVBoxLayout(files_scanned)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(4)

        label = QLabel("ISSUES SOLVED")
        label.setObjectName("solvedTitle")
        label.setAlignment(Qt.AlignCenter)

        self.label_issues_solved = QLabel(str(self.issues_solved))
        self.label_issues_solved.setObjectName("solvedAmount")
        self.label_issues_solved.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(label)
        card_layout.addWidget(self.label_issues_solved)

        cards_layout.addWidget(files_scanned)
        main_layout.addLayout(cards_layout)
        # </editor-fold>

        separator = QSpacerItem(20, 20)
        main_layout.addItem(separator)

        # table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["File", "Issue", "Info"])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 300)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_row_selected)

        main_layout.addWidget(self.table)

        separator = QSpacerItem(20, 20)
        main_layout.addItem(separator)

        # bottom btns
        btns_row = QHBoxLayout()
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.setObjectName("renameButton")
        self.rename_btn.clicked.connect(self.rename_pressed)
        self.rename_btn.setEnabled(False)
        # self.rename_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #2b2b2b;
        #         color: #888888;
        #         border: 1px solid #3a3a3a;
        #         border-radius: 4px;
        #         padding: 4px 8px;
        #     }
        #     QPushButton:enabled {
        #         background-color: #EAF3DE;
        #         color: #27500A;
        #         border: 1px solid #C0DD97;
        #         border-radius: 4px;
        #     }
        #     QPushButton:enabled:hover {
        #         background-color: #C0DD97;
        #         color: #27500A;
        #     }
        # """)

        self.move_btn = QPushButton("Move")
        self.move_btn.setObjectName("moveButton")
        self.move_btn.clicked.connect(self.move_pressed)
        self.move_btn.setEnabled(False)
        # self.move_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #2b2b2b;
        #         color: #888888;
        #         border: 1px solid #3a3a3a;
        #         border-radius: 4px;
        #         padding: 4px 8px;
        #     }
        #     QPushButton:enabled {
        #         background-color: #EAF3DE;
        #         color: #27500A;
        #         border: 1px solid #C0DD97;
        #         border-radius: 4px;
        #     }
        #     QPushButton:enabled:hover {
        #         background-color: #C0DD97;
        #         color: #27500A;
        #     }
        # """)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.clicked.connect(self.delete_pressed)
        # self.delete_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #d0d0d0;
        #         color: #888888;
        #         border: 1px solid #b0b0b0;
        #         border-radius: 4px;
        #         padding: 4px 8px;
        #     }
        #     QPushButton:enabled {
        #         background-color: #f3e6de;
        #         color: #50180a;
        #         border: 1px solid #ddad97;
        #         border-radius: 4px;
        #     }
        #     QPushButton:enabled:hover {
        #         background-color: #ddad97;
        #         color: #50180a;
        #     }
        # """)

        self.ignore_btn = QPushButton("Ignore")
        self.ignore_btn.setObjectName("ignoreButton")
        self.ignore_btn.clicked.connect(self.ignore_pressed)
        # self.ignore_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #d0d0d0;
        #         color: #888888;
        #         border: 1px solid #b0b0b0;
        #         border-radius: 4px;
        #         padding: 4px 8px;
        #     }
        #     QPushButton:enabled {
        #         background-color: #f3f0de;
        #         color: #4a3a0a;
        #         border: 1px solid #ddd097;
        #         border-radius: 4px;
        #     }
        #     QPushButton:enabled:hover {
        #         background-color: #ddd097;
        #         color: #4a3a0a;
        #     }
        # """)

        self.explorer_btn = QPushButton("Open in Explorer")
        self.explorer_btn.setObjectName("explorerButton")
        # self.explorer_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #d0d0d0;
        #         color: #888888;
        #         border: 1px solid #b0b0b0;
        #         border-radius: 4px;
        #         padding: 4px 8px;
        #     }
        #     QPushButton:enabled {
        #         background-color: #2b2b2b;
        #         color: white;
        #         border: 1px solid #3a3a3a;
        #         border-radius: 4px;
        #     }
        #     QPushButton:enabled:hover {
        #         background-color: #313131;
        #         color: white;
        #     }
        # """)
        self.explorer_btn.clicked.connect(self.explorer_pressed)

        btns_row.addWidget(self.explorer_btn)
        btns_row.addWidget(self.rename_btn)
        btns_row.addWidget(self.move_btn)
        btns_row.addWidget(self.ignore_btn)
        btns_row.addWidget(self.delete_btn)

        main_layout.addLayout(btns_row)

    def pick_scan_directory(self):
        """
        Open a folder picker dialog and populate the 'directory to scan' field.
        """
        scan_directory = QFileDialog().getExistingDirectory()
        self.directory_to_scan.setText(scan_directory)

    def pick_config_file(self):
        """
        Open a file picker dialog, populate the config file field, and immediately load the selected config.
        """
        config_file = QFileDialog().getOpenFileName()
        self.config_file.setText(config_file[0])
        self.scanner.load_config(config_file[0])

    def reload_config(self):
        """
        Re-load the config from the currently entered path. Shows an error dialog if loading fails.
        """
        error = self.scanner.load_config(self.config_file.text())
        if error:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error loading config")
            msg.setText(error)
            msg.exec()
        self.scanner.config = None
        self.btn_game_ready.setChecked(True)
        self.btn_source.setChecked(False)

    def insert_issue_row(self, filename, issue, info):
        """
        Append a new row to the issues table with the given filename, issue type, and info.
        :param filename: Name of the file
        :param issue: Issue that's related to the file
        :param info: More info about the issue of the file
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(filename))
        self.table.setItem(row, 1, QTableWidgetItem(issue))
        self.table.setItem(row, 2, QTableWidgetItem(info))

    def on_row_selected(self):
        """
        Handle table selection changes. Update the currently selected issue and refreshes the enabled state of the
        action buttons.
        """
        selected_rows = self.table.selectedItems()

        if not selected_rows:
            return

        row = self.table.currentRow()
        self.row_selected = self.issues[row]
        self.update_btns()

    def update_btns(self):
        """
        Enable or disable the Rename and Move buttons based on the issue types of all currently selected rows. Buttons
        are only enabled when all selected rows share a compatible issue type.
        """
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
        elif all(issue == "Prefix" or issue == "Suffix" or issue == "Naming" for issue in selected_issues):
            self.rename_btn.setEnabled(True)
            self.move_btn.setEnabled(False)
        elif all(issue == "Image size" for issue in selected_issues):
            self.rename_btn.setEnabled(False)
            self.move_btn.setEnabled(False)
        else:
            self.rename_btn.setEnabled(False)
            self.move_btn.setEnabled(False)

    def scan_executed(self):
        """
        Clear previous results, run a fresh scan on the configured directory, and populate the table with any issues
        found. Shows an error dialog on failure.
        :return:
        """
        # resetting from previous scan
        self.table.setRowCount(0)
        self.issues.clear()
        self.issues_solved = 0

        nr_files = 0
        result = None

        if self.btn_game_ready.isChecked():
            nr_files, result = self.scanner.scan(self.directory_to_scan.text(), "game_ready")
        elif self.btn_source.isChecked():
            nr_files, result = self.scanner.scan(self.directory_to_scan.text(), "source")

        if type(result) == str:
            QMessageBox.warning(None, "Error reading file path", result)
            return
        else:
            self.files_scanned = nr_files
            self.problems_found = len(result)
            self.reload_result_row()

            self.issues = result
            for issue in result:
                self.insert_issue_row(issue.filename, issue.issue, issue.info)

    def reload_result_row(self):
        """
        Refresh the three stat cards to reflect current values of files scanned, issues found, and issues solved.
        """
        self.label_scanned_files.setText(str(self.files_scanned))
        self.label_issues_found.setText(str(self.problems_found))
        self.label_issues_solved.setText(str(self.issues_solved))

    def explorer_pressed(self):
        """
        Collect filepaths of all selected rows and open them in Windows Explorer.
        """
        selected_rows = self.table.selectionModel().selectedRows()
        files = []
        for row in selected_rows:
            row_nr = row.row()
            issue_filepath = self.issues[row_nr].filepath
            files.append(issue_filepath)

        self.scanner.open_in_explorer(files)

    def rename_pressed(self):
        """
        Trigger the rename flow for all selected rows (in reverse order to preserve row indices) and remove successfully
        renamed rows from the table.
        """
        selected_rows = self.table.selectionModel().selectedRows()
        for row in reversed(selected_rows):
            row_nr = row.row()
            success = self.scanner.rename_file(self.issues[row_nr])
            if success:
                self.remove_row_on_success(row_nr)

    def move_pressed(self):
        """
        Trigger the move flow for all selected rows (in reverse order) and remove successfully moved rows from the
        table.
        """
        selected_rows = self.table.selectionModel().selectedRows()
        for row in reversed(selected_rows):
            row_nr = row.row()
            success = self.scanner.move_file(self.issues[row_nr], self.directory_to_scan.text())
            if success:
                self.remove_row_on_success(row_nr)

    def ignore_pressed(self):
        """
        Remove all selected rows from the table and issue list without taking any action.
        """
        if self.row_selected is None:
            return

        rows = self.table.selectionModel().selectedRows()
        for row in reversed(rows):
            row_nr = row.row()
            self.table.removeRow(row_nr)
            self.issues.pop(row_nr)
            self.row_selected = None

    def delete_pressed(self):
        """
        Trigger the delete flow for all selected rows.
        """
        selected_rows = self.table.selectionModel().selectedRows()

        for row in reversed(selected_rows):
            row_nr = row.row()
            success = self.scanner.delete_files(self.issues[row_nr])
            if success:
                self.remove_row_on_success(row_nr)

    def remove_row_on_success(self, row):
        """
        Remove a row from the table and issue list after a successful action, update the issue counters, and refresh
        the stat cards and button states.
        :param row: Row to remove from the table
        """
        self.table.removeRow(row)
        self.issues.pop(row)
        self.issues_solved += 1
        self.problems_found -= 1
        self.reload_result_row()
        self.update_btns()

    def closeEvent(self, event):
        """
        Save the current UI state to disk when the window is closed.
        """
        self.scanner.save_ui(
            self.directory_to_scan.text(),
            self.config_file.text(),
            self.issues,
            self.files_scanned,
            self.issues_solved,
            self.btn_game_ready.isChecked(),
            self.btn_source.isChecked(),
        )
        event.accept()