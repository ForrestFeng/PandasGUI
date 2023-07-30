import os
import re
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal

import logging

from pandasgui.store import PandasGuiDataFrameStore
from typing import Dict
from typing import List

logger = logging.getLogger(__name__)

from pandasgui.widgets.column_viewer import FlatDraggableTree

plugins_directory = r"C:\Users\Forrest\Code\py311_pandasgui\PandasGUI\pandasgui\plugins\titanic"


class AutoFilterTree(FlatDraggableTree):
    onAutoFilterChangedEvent = pyqtSignal(dict)
    def __init__(self):
        super().__init__()

        # Header
        self.prefix_header = ['Class', 'Name']
        self.prefix_rows = None
        # Set up the tree widget properties
        self.button_groups = []

        # Tracking the active fitlers
        self.auto_fitlers: Dict[List, int] = {}

    def set_prefix_header(self, prefix_header):
        self.prefix_header = prefix_header

    def set_prefix_rows(self, prefix_rows_list: []):
        self.prefix_rows = prefix_rows_list

    def add_items_with_radio_buttons(self, radio_columns=3):
        # must have at least 3 columns

        assert(radio_columns > 0)
        self.setColumnCount(radio_columns + len(self.prefix_header))
        filter_headers = [f"{i}" for i in range(radio_columns)]
        self.setHeaderLabels(self.prefix_header + filter_headers)
        self.auto_fitlers: Dict[tuple, int] = {} # tupele => int

        for row, prefix in enumerate(self.prefix_rows):
            item = QtWidgets.QTreeWidgetItem(self, prefix[1:])

            self.addTopLevelItem(item)

            button_group = QtWidgets.QButtonGroup(self)
            button_group.setProperty("prefix", tuple(prefix))
            button_group.setProperty("row", row)
            button_group.setProperty("last_checked_id", -1)
            button_group.buttonClicked.connect(self.on_radio_button_clicked)
            self.button_groups.append(button_group)

            # Tracking active filters, initialize with No Active
            # convert prefix list to tuple to fix TypeError: unhashable type: 'list'
            self.auto_fitlers[tuple(prefix)] = -1

            radio_button_cols = radio_columns
            for i in range(radio_button_cols):
                radio_button = QtWidgets.QRadioButton('》')
                # add button with id
                button_group.addButton(radio_button, id=i)
                self.setItemWidget(item, len(prefix[1:]) + i, radio_button)

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
            self.auto_fitlers[group.property('prefix')] = -1
        else:
            # for other case set Exclusive to True
            group.setExclusive(True)

        if button.isChecked():
            group.setProperty("last_checked_id", group.id(button))
            self.auto_fitlers[group.property('prefix')] = group.id(button)
            print(f"Remember the checked button {group.property('prefix')} at ({group.property('row')},{group.id(button)})")

        print(
            f"{group.property('prefix')} at ({group.property('row')},{group.id(button)}) Checked: {button.isChecked()}")



        # Logic to move deactive filter(with all-off-radio-button) below the active ones.


        # logic to collect filter_settings


        # emit auto filter chagned signal
        self.onAutoFilterChangedEvent.emit(self.auto_fitlers)


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

class AutoFilterViewer(QtWidgets.QWidget):

    def __init__(self, pgdf: PandasGuiDataFrameStore, plugins_directory: str = plugins_directory):
        super().__init__()
        pgdf = PandasGuiDataFrameStore.cast(pgdf)
        self.pgdf = pgdf

        self.plugins_directory = plugins_directory
        self.module_methods = None  # dict module:types.ModuleType => methods: (class_name: str, method_name: str)

        self.tree: FlatDraggableTree = AutoFilterTree()
        self.tree.setDragEnabled(True)
        self.tree.setDefaultDropAction(Qt.CopyAction)

        self.display_module = False
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)

        # Search box
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.textChanged.connect(self.filter)

        self.source_tree_layout = QtWidgets.QVBoxLayout()
        self.source_tree_layout.addWidget(self.search_bar)
        self.source_tree_layout.addWidget(self.tree)
        self.setLayout(self.source_tree_layout)

        # Load filters from plugins directory
        self.load_plugins()
        self.refresh()

        # link the singal
        self.tree.onAutoFilterChangedEvent.connect(self.autoFilterChagned)


    @QtCore.pyqtSlot(dict)
    def autoFilterChagned(self, auto_filters: dict): #Dict[List, int]
        # the filter_setting is a list of filters
        # [ [f1, f2], [f3, f4], [f5] ]
        self.pgdf.set_auto_filter(auto_filters)


    def load_plugins(self):
        from pandasgui.automation.filters_loader import find_module_methods
        self.module_methods = find_module_methods(self.plugins_directory)

    def refresh(self):
        filter_prefix_rows = []
        for module, methods in self.module_methods.items():
            for class_name, method_name in methods:
                filter_prefix_rows.append([module, class_name, method_name])

        self.tree.set_prefix_rows(filter_prefix_rows)
        self.tree.add_items_with_radio_buttons(3)

        # Depends on Search Box and Source list
        self.filter()
        self.tree.apply_tree_settings()

    def filter(self):
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.child(i)
            child.setHidden(True)

        items = self.tree.findItems(f".*{self.search_bar.text()}.*",
                                    Qt.MatchRegExp | Qt.MatchRecursive)
        for item in items:
            item.setHidden(False)




if __name__ == "__main__":
    # Create a QtWidgets.QApplication instance or use the existing one if it exists
    app = QtWidgets.QApplication(sys.argv)


    afv = AutoFilterViewer()
    afv.show()

    app.exec_()
