from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QProgressBar, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QFileDialog
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Directory Scanner")

        self.draw_interface()

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

        config_row.addWidget(label_config)
        config_row.addWidget(self.config_file)
        config_row.addWidget(browse_button_config)
        config_row.addWidget(reload_btn)
        main_layout.addLayout(config_row)

        # scan button
        scan_btn = QPushButton("Scan")
        main_layout.addWidget(scan_btn)

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

        filename = "rock_diffuse.png"
        issue = "Missing prefix"
        info = "rename to → T_rock_diffuse.png"
        self.insert_issue_row(filename, issue, info)

        main_layout.addWidget(self.table)

        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

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


