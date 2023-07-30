
import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class CheckBoxGrid(QTableWidget):
    def __init__(self):
        super().__init__()

        # Set up the table widget properties
        self.setRowCount(3)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels([f"Column {i+1}" for i in range(4)])

        # Add checkboxes to each cell
        self.add_checkboxes(3, 4)

    def add_checkboxes(self, rows, columns):
        for row in range(rows):
            for col in range(columns):
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
                self.setItem(row, col, item)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    # Create the CheckBoxGrid widget
    grid_widget = CheckBoxGrid()
    layout.addWidget(grid_widget)

    window.show()
    sys.exit(app.exec_())
