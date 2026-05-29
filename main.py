from PySide6.QtWidgets import QApplication
from scanner_ui import MainWindow

app = QApplication()
app.setStyle("Fusion")
app.setPalette(app.style().standardPalette())
window = MainWindow()
window.show()
app.exec()