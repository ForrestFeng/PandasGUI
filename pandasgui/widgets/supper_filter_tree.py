

# Supper filter is a filter view it allow user to load predifind filters in to the viewer and user can
# simply click the radio buttons to apply fitlers on the data frame.
# it is faster, easy to use, support and or logic

import os
import re
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal
from pandasgui.automation.filters_loader import PgPluginLoader
import pandas as pd
import logging

from typing import Dict
import types


logger = logging.getLogger(__name__)

from pandasgui.widgets.column_viewer import FlatDraggableTree



class SupperFilterModel:

    def __init__(self):
        self.plugins_loader = PgPluginLoader()

    def apply_supper_filter(self, module: types.ModuleType, class_name:str, method_name:str, dataframe: pd.DataFrame):
        return self.plugins_loader.run_static_methods(module, class_name, method_name, dataframe)

    def get_module_class_method_list(self):
        return self.plugins_loader.get_module_class_method_list()


class SupperFilterTree(FlatDraggableTree):
    onSupperFilterChangedEvent = pyqtSignal(dict, list, SupperFilterModel)
    FILTER_LEVEL = 6
    def __init__(self):
        super().__init__()
        self.model = SupperFilterModel()

        # Header
        self.module_method_header = ['Module', 'Class', 'Name']

        # Set up the tree widget properties
        self.radio_groups = []
        self.checkbox_group = None

        # self.my_checkbox
        self.checkbox_buttons = {}
        self.radio_buttons = {}

        # Tracking the all supper filters
        self.supper_filters: Dict[tuple, int] = {}

        # Tracking the active inspecting index
        self.inspecting_index_arg = [-1, -1]

        # Init
        self.add_items_with_radio_buttons()

    def get_model(self):
        return self.model

    def refresh_supper_filter_tree(self, enabled_ands, inspecting_index_arg):
        # Reset Button Text
        for checkbox in self.checkbox_buttons.values():
            checkbox.setText("*")
        for radio_button in self.radio_buttons.values():
            radio_button.setText("》")

        # Update Button Text with Number
        for rank, ors in enumerate(enabled_ands):
            m_c_m, radio_index = "", -1
            for or_cell in ors[:-1]:
                m_c_m, radio_index = or_cell[0]
                self.radio_buttons[(m_c_m, radio_index)].setText(f"{or_cell[1]}")

            output, input = ors[-1][0], ors[-1][1]
            if inspecting_index_arg[1] != -1:
                self.checkbox_buttons[radio_index].setText(f"{inspecting_index_arg[1]}")
            elif output != -1:
                self.checkbox_buttons[radio_index].setText(f"{output}")

    def add_items_with_radio_buttons(self, radio_columns=FILTER_LEVEL):
        # Set header
        assert(radio_columns > 0)
        self.setColumnCount(radio_columns + len(self.module_method_header))
        levels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
        filter_headers = [f"{i}" for i in levels[:radio_columns]]
        self.setHeaderLabels(self.module_method_header + filter_headers)
        self.supper_filters: Dict[tuple, int] = {}  # tuple => int

        # Add highlight item at the top
        module_class_method = ('Builtin ', 'Result DF', 'Inspecting')
        highlight_item = QtWidgets.QTreeWidgetItem(self, module_class_method)
        self.addTopLevelItem(highlight_item)
        checkbox_group = QtWidgets.QButtonGroup(self)
        module_class_method_list = self.model.get_module_class_method_list()
        assert (len(module_class_method_list) > 0)

        for i in range(radio_columns):
            checkbox_button = QtWidgets.QCheckBox('*')
            self.checkbox_buttons[i] = checkbox_button
            # add button with id
            checkbox_group.addButton(checkbox_button, id=i)
            checkbox_group.setProperty("prefix", module_class_method)
            checkbox_group.setProperty("row", 0)
            checkbox_group.setProperty("last_checked_id", -1)
            self.setItemWidget(highlight_item, len(module_class_method_list[0]) + i, checkbox_button)

        checkbox_group.buttonClicked.connect(self.on_highlight_button_clicked)
        self.checkbox_group = checkbox_group

        # Add filter items after highlight
        last_module_class_method = None
        for row, module_class_method in enumerate(module_class_method_list):
            m_c_m = [module_class_method[0].__name__,
                                        module_class_method[1], module_class_method[2]]
            if last_module_class_method is not None:
                if m_c_m[0] == last_module_class_method[0]:
                    m_c_m[0] = ""
                if m_c_m[1] == last_module_class_method[1]:
                    m_c_m[1] = ""
            item = QtWidgets.QTreeWidgetItem(self, m_c_m)

            # Add itm in top level
            self.addTopLevelItem(item)

            # make all radio button in the button_group
            radio_group = QtWidgets.QButtonGroup(self)

            radio_group.setProperty("prefix", module_class_method)
            radio_group.setProperty("row", row+1)
            radio_group.setProperty("last_checked_id", -1)
            radio_group.buttonClicked.connect(self.on_radio_button_clicked)
            self.radio_groups.append(radio_group)

            # Tracking active filters, initialize with No Active
            self.supper_filters[module_class_method] = -1

            for i in range(radio_columns):
                radio_button = QtWidgets.QRadioButton('》')
                # add button with id
                radio_group.addButton(radio_button, id=i)
                self.setItemWidget(item, len(module_class_method) + i, radio_button)
                self.radio_buttons[(module_class_method, i)] = radio_button

            # remember it for compare
            last_module_class_method = [module_class_method[0].__name__,
                                        module_class_method[1], module_class_method[2]]


    def on_highlight_button_clicked(self, button: QtWidgets.QCheckBox):
        group = button.group()
        if group.property("last_checked_id") == group.id(button):
            logger.debug(f"Inspecting Checkbox: checked button changes to UNCKECKED {group.property('prefix')[1:]} at ({group.property('row')},{group.id(button)})")
            # if this button state changes from checked to unchecked, set exclusive false
            group.setExclusive(False)
            button.setChecked(False)
            group.setProperty("last_checked_id", -1)
            self.inspecting_index_arg = [-1, -1]
        else:
            # for other case set Exclusive to True
            group.setExclusive(True)

        if button.isChecked():
            group.setProperty("last_checked_id", group.id(button))
            self.inspecting_index_arg = [group.id(button), -1]
            logger.debug(f"Inspecting Checkbox: remember the checked button {group.property('prefix')[1:]} at ({group.property('row')},{group.id(button)})")

        logger.debug(
            f"Inspecting Checkbox: {group.property('prefix')[1:]} at ({group.property('row')},{group.id(button)}) Checked: {button.isChecked()}")


        # emit checkbox change
        self.onSupperFilterChangedEvent.emit(self.supper_filters, self.inspecting_index_arg, self.model)

    def on_radio_button_clicked(self, button: QtWidgets.QRadioButton):
        # GUI logic to make the radio button on off as designed.
        # We allow the radio button to set all off statue.
        # Once a button is checked, we only allow one button is checked.
        group = button.group()

        if group.property("last_checked_id") == group.id(button):
            logger.debug(f"Filter RadioButton: checked button changes to UNCKECKED {group.property('prefix')[1:]} at ({group.property('row')},{group.id(button)})")
            # if this button state changes from checked to unchecked, set exclusive false
            group.setExclusive(False)
            button.setChecked(False)
            group.setProperty("last_checked_id", -1)
            self.supper_filters[group.property('prefix')] = -1
        else:
            # for other case set Exclusive to True
            group.setExclusive(True)

        if button.isChecked():
            group.setProperty("last_checked_id", group.id(button))
            self.supper_filters[group.property('prefix')] = group.id(button)
            logger.debug(f"Filter RadioButton: remember the checked button {group.property('prefix')[1:]} at ({group.property('row')},{group.id(button)})")

        logger.debug(
            f"Filter RadioButton: {group.property('prefix')[1:]} at ({group.property('row')},{group.id(button)}) Checked: {button.isChecked()}")

        # emit filter changed signal
        self.onSupperFilterChangedEvent.emit(self.supper_filters, self.inspecting_index_arg, self.model)


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

