##########################################
import sys
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

class CheckBoxTree(QTreeWidget):
    def __init__(self):
        super().__init__()

        # Header
        self.pre_fix_header = ['Class', 'Name']
        # Set up the tree widget properties
        self.button_groups = []

        # Add items with checkboxes
        self.add_items_with_radio_buttons(2, 5)

    def add_items_with_radio_buttons(self, rows, columns):
        # must have at least 3 columns

        assert(columns > len(self.pre_fix_header))
        self.setColumnCount(columns)
        filter_headers = [f"{i}" for i in range(columns - len(self.pre_fix_header))]
        self.setHeaderLabels(self.pre_fix_header + filter_headers)

        for row in range(rows):
            pre_fix = [f"Class {row}", f"Filter {row}"]
            item = QTreeWidgetItem(self, pre_fix)

            self.addTopLevelItem(item)

            button_group = QtWidgets.QButtonGroup(self)
            button_group.setProperty("prefix", pre_fix)
            button_group.setProperty("row", row)
            button_group.setProperty("last_checked_id", -1)
            button_group.buttonClicked.connect(self.on_radio_button_clicked)
            self.button_groups.append(button_group)

            radio_button_cols = columns - len(pre_fix)
            for i in range(radio_button_cols):
                radio_button = QtWidgets.QRadioButton('》')
                # add button with id
                button_group.addButton(radio_button, id=i)
                self.setItemWidget(item, len(pre_fix) + i, radio_button)

        print(self.button_groups)

    def on_radio_button_clicked(self, button: QtWidgets.QRadioButton):
        # GUI logic to make the radio button on off as designed.
        # We allow the radio button to set all off statue.
        # Once a button is checked, we only allow one button is checked.
        group = button.group()

        if group.property("last_checked_id") == group.id(button):
            (f"Checked button changes to UNCKECKED {group.property('prefix')} at ({group.property('row')},{group.id(button)})")
            # if this button state changes from checked to unchecked, set exclusive false
            group.setExclusive(False)
            button.setChecked(False)
            group.setProperty("last_checked_id", -1)
        else:
            # for other case set Exclusive to True
            group.setExclusive(True)

        if button.isChecked():
            group.setProperty("last_checked_id", group.id(button))
            print(f"Remember the checked button {group.property('prefix')} at ({group.property('row')},{group.id(button)})")

        print(
            f"{group.property('prefix')} at ({group.property('row')},{group.id(button)}) Checked: {button.isChecked()}")


        # Logic to move deactive filter(with all-off-radio-button) below the active ones.





    def add_new_column(self, column_label):
        # Get the current column count
        current_column_count = self.columnCount()

        # Add the new column label
        header_labels = [self.headerItem().text(i) for i in range(current_column_count)]
        header_labels.append(column_label)

        # Set the updated header labels with the new column
        self.setHeaderLabels(header_labels)

    def delete_last_column(self):
        # Get the current column count
        current_column_count = self.columnCount()

        # Check if there is at least one column
        if current_column_count > 1:
            # Remove the last column using removeColumn()
            self.removeColumn(current_column_count - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    window.setFixedWidth(900)
    layout = QVBoxLayout(window)

    # Create the CheckBoxTree widget
    tree_widget = CheckBoxTree()
    layout.addWidget(tree_widget)

    # Create a button to add a new column
    add_column_button = QPushButton("Add Column")
    add_column_button.clicked.connect(lambda: tree_widget.add_new_column("New Column"))
    layout.addWidget(add_column_button)

    # Create a button to delete the last column
    delete_column_button = QPushButton("Delete Last Column")
    delete_column_button.clicked.connect(tree_widget.delete_last_column)
    layout.addWidget(delete_column_button)

    window.show()
    sys.exit(app.exec_())
