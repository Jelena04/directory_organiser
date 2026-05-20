from PySide6.QtWidgets import (QMainWindow,QMessageBox, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QProgressBar, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                               QCheckBox, QFileDialog)
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
        self.table = None

        self.draw_interface()
        self.restore_ui()

        self.issues = []

    def draw_interface(self):
        main_container = QWidget()
        self.setCentralWidget(main_container)
        main_layout = QVBoxLayout(main_container)

        # to scan row
        to_scan_row = QHBoxLayout()

        label_to_scan = QLabel("Directory to scan")
        label_to_scan.setFixedWidth(100)
        self.directory_to_scan = QLineEdit()
        self.directory_to_scan.setFixedWidth(300)
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
        self.config_file.setFixedWidth(300)
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
        files_scanned = 0
        problems_found = 0
        result_label = QLabel(f"Result: {files_scanned} files scanned - {problems_found} issues found")
        main_layout.addWidget(result_label)

        # table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["✔", "File", "Issue", "Info"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

        main_layout.addWidget(self.table)

        # bottom btns
        btns_row = QHBoxLayout()
        rename_btn = QPushButton("Rename")
        move_btn = QPushButton("Move")
        delete_btn = QPushButton("Delete")
        ignore_btn = QPushButton("Ignore")
        explorer_btn = QPushButton("Open in Explorer")

        btns_row.addWidget(rename_btn)
        btns_row.addWidget(move_btn)
        btns_row.addWidget(delete_btn)
        btns_row.addWidget(ignore_btn)
        btns_row.addWidget(explorer_btn)

        main_layout.addLayout(btns_row)

    def insert_issue_row(self, filename, issue, info):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # checkbox cell (needs a wrapper widget to center it)
        checkbox_widget = QWidget()
        checkbox = QCheckBox()
        layout = QHBoxLayout(checkbox_widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table.setCellWidget(row, 0, checkbox_widget)

        # text cells
        self.table.setItem(row, 1, QTableWidgetItem(filename))
        self.table.setItem(row, 2, QTableWidgetItem(issue))
        self.table.setItem(row, 3, QTableWidgetItem(info))

    def on_header_clicked(self, column):
        if column == 0:
            # toggle all checkboxes
            for row in range(self.table.rowCount()):
                checkbox_widget = self.table.cellWidget(row, 0)
                checkbox = checkbox_widget.findChild(QCheckBox)
                checkbox.setChecked(not checkbox.isChecked())

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
        result = self.scanner.scan(self.directory_to_scan.text())
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