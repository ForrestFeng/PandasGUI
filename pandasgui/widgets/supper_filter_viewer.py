
import numpy
import sys
from typing import Dict, List

from pandasgui.widgets.column_viewer import FlatDraggableTree
from pandasgui.widgets.supper_filter_tree import SupperFilterTree, SupperFilterModel
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

import logging

from pandasgui.store import PandasGuiDataFrameStore

logger = logging.getLogger(__name__)


class SupperFilterViewer(QtWidgets.QWidget):

    def __init__(self, pgdf: PandasGuiDataFrameStore = None):
        super().__init__()
        self.pgdf = pgdf

        self.tree: FlatDraggableTree = SupperFilterTree()
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
        self.refresh()

        # link the singal
        self.tree.onSupperFilterChangedEvent.connect(self.supperFilterChagned)

    @QtCore.pyqtSlot(dict, list, SupperFilterModel)
    def supperFilterChagned(self, supper_filters: Dict[tuple, int], inspecting_index_arg: [int, int], model: SupperFilterModel):

        # Convert supper_filters from list of Dict[Fn, idx]
        # to InOutArg in the form of
        # [ [[(F1, idx), n], [(F2, idx), n]],
        #   [[(F3, idx), n]],
        #   [[(F4, idx), n], [(F5, idx), n]]
        # ]

        # The Fn stands for filter full name m_c_m, idx is the filter level in 0 to max_level
        # The n here is the number rows selected for the corresponding filter.
        # The InOutArg is for both input and output.

        # the supper filter is a dict with (module, class, method) => radio_index
        # radio_index = -1: filter is inactive
        # radio_index in [0, x]: filter is active
        # radio_index of the same radio_index, the filter results apply or logic (|)
        # radio_index of low and higher, the results apply and logic (&)

        keys = list(supper_filters.keys())
        values = list(supper_filters.values())
        sorted_value_index = numpy.argsort(values)
        sorted_dict = {keys[i]: values[i] for i in sorted_value_index}
        logger.debug(sorted_dict)

        # sorted dict with radio_index from low to high
        enabled_ors = []
        enabled_ands = []
        for i in sorted_value_index:
            m_c_m_key = keys[i]
            radio_index = values[i]
            # Only care the active ones
            if radio_index >= 0:
                if len(enabled_ors) == 0:
                    enabled_ors.append([(m_c_m_key, radio_index), -1])
                else: # > 0
                    if enabled_ors[-1][0][1] == radio_index:
                        enabled_ors.append((m_c_m_key, radio_index))
                    elif enabled_ors[-1][0][1] < radio_index:
                        # save radio_index ends, add it to enabled_ands list
                        enabled_ands.append(enabled_ors)
                        # then create new ords
                        enabled_ors = [[(m_c_m_key, radio_index), -1]]
                    else:
                        raise Exception(f"The radio_index order is wrong {keys} {values}")
        # add the last enabled_ors to enabled_ands
        enabled_ands.append(enabled_ors)
        logger.debug(enabled_ands)

        if self.pgdf is not None:
            self.pgdf.apply_supper_filter(enabled_ands, inspecting_index_arg, model)
            print(enabled_ands)
            print(inspecting_index_arg)


    def refresh(self):
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
    sfv = SupperFilterViewer()
    sfv.setFixedWidth(900)
    sfv.setFixedHeight(500)
    sfv.show()

    app.exec_()


