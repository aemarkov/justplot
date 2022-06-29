import logging
from dataclasses import dataclass
from typing import Any, List, NoReturn, Sequence, Union, cast

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, pyqtSignal
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem

from .model import FilePlot


# Workaround to print QModelIndex for debug purposes
def mi_repr(self: QModelIndex) -> str:
    return f'Index({self.row()}, {self.column()}, {type(self.internalPointer()).__name__})'


QModelIndex.__repr__ = mi_repr


@dataclass
class _ChildData:
    """Internal data structure for child nodes (plots)"""
    parent: '_ParentData'
    plot: PlotDataItem
    is_visible: bool


class _ParentData:
    """Internal data structure for parent nodes (files)"""
    def __init__(self, file_plot: FilePlot):
        self.path = file_plot.path
        self.children = [_ChildData(self, plot, True) for plot in file_plot.plots]
        self.is_visible = True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, _ParentData):
            return False
        return self.path == o.path and self.children == o.children


_NodeData = Union[None, _ParentData, _ChildData]


@dataclass(frozen=True)
class PlotVisibleChanged:
    """Struct used to notify visibility changes"""
    is_visible: bool
    plot: PlotDataItem


class PlotTreeModel(QAbstractItemModel):

    plot_visible_changed = pyqtSignal(PlotVisibleChanged)
    plot_cleared = pyqtSignal()

    """
    Model to store plot data: list of files with list of plots (data series)
    in the each file. So, this model is forced to have two items depth
    Root (-1, -1, None)
       |
       |--File (row, 0, <_ParentData>)
       |     |--Plot (row, 0, <_ChildData>)
      ...    |--Plot (row, 0, <_ChildData>)
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._files: List[_ParentData] = []

    def add_file(self, file: FilePlot):
        logging.debug('Add file %s to GraphView', file.path)
        index = len(self._files)
        self.beginInsertRows(QModelIndex(), index, index)
        self._files.append(_ParentData(file))
        self.endInsertRows()

    def delete_plot(self, index: QModelIndex):
        logging.debug('Delete plot with index %s', index)

        if not index.isValid():
            return

        data = _get_data(index)
        parent = index.parent()
        if isinstance(data, _ParentData):
            # Notify view to remove all children plots
            self.beginRemoveRows(parent, index.row(), index.row())
            for child in data.children:
                self.visibility_changed(False, child.plot)
            self._files.remove(data)
            self.endRemoveRows()
        elif isinstance(data, _ChildData):
            # Get parent and remove parent from childre
            parent_data = _get_data(parent)
            if not isinstance(parent_data, _ParentData):
                _raise_data_err(parent_data)

            if index.row() >= len(parent_data.children):
                logging.warn('Selected index is out of range')
                return

            self.beginRemoveRows(parent, index.row(), index.row())
            self.visibility_changed(False, data.plot)
            parent_data.children.remove(data)
            self.endRemoveRows()
        else:
            _raise_data_err(data)


    def delete_all(self):
        logging.debug('Delete all plots')
        self.beginResetModel()
        self._files = []
        self.plot_clear()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex) -> int:
        if parent == QModelIndex():
            return len(self._files)

        data = _get_data(parent)
        if isinstance(data, _ParentData):
            return len(data.children)
        elif isinstance(data, _ChildData):
            return 0
        else:
            _raise_data_err(data)

    def columnCount(self, parent: QModelIndex) -> int:
        if parent == QModelIndex():
            return 1
        data = _get_data(parent)
        return 1 if data is not None else 0

    def data(self, index: QModelIndex, role: int) -> Any:
        if not index.isValid():
            return None

        data = _get_data(index)

        if isinstance(data, _ParentData):
            display = data.path.name
        elif isinstance(data, _ChildData):
            display = data.plot.name()
        else:
            _raise_data_err(data)

        if role == Qt.DisplayRole:
            return display
        elif role == Qt.CheckStateRole:
            return _checked(data.is_visible)

    def setData(self, index: QModelIndex, value: Any, role: int) -> bool:
        if not index.isValid():
            return False
        if role != Qt.CheckStateRole:
            return False

        data = _get_data(index)
        if isinstance(data, _ParentData):
            data.is_visible = value == Qt.Checked
            logging.debug('File node %s is checked (visible=%d)', index, data.is_visible)
            # Check/uncheck all children of this node
            for child_index in self._get_children_index(data):
                self.setData(child_index, value, role)
        elif isinstance(data, _ChildData):
            data.is_visible = value == Qt.Checked
            logging.debug('Plot node %s is checked (visible=%d)', index, data.is_visible)
            self.visibility_changed(data.is_visible, data.plot)
        else:
            _raise_data_err(data)

        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section: int, orientation: Qt.Orientation,
            role: int) -> Any:
        if orientation != Qt.Horizontal or role != Qt.DisplayRole:
            return 'Plots'

    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if parent == QModelIndex():
            return self.createIndex(row, column, self._files[row])
        data = _get_data(parent)
        if isinstance(data, _ParentData):
            return self.createIndex(row, column, data.children[row])
        elif isinstance(data, _ChildData):
            return QModelIndex()
        else:
            _raise_data_err(data)

    def parent(self, index: QModelIndex) -> QModelIndex:
        if index == QModelIndex():
            return QModelIndex()

        data = _get_data(index)
        if isinstance(data, _ParentData):
            return QModelIndex()
        elif isinstance(data, _ChildData):
            return self.createIndex(index.row(), index.column(), data.parent)
        else:
            _raise_data_err(data)

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

    def _get_children_index(self, data: _ParentData) -> Sequence[QModelIndex]:
        return [self.createIndex(i, 0, child) for i, child in enumerate(data.children)]

    def visibility_changed(self, is_visible: bool, plot: PlotDataItem):
        self.plot_visible_changed.emit(PlotVisibleChanged(is_visible, plot))

    def plot_clear(self):
        self.plot_cleared.emit()


def _get_data(index: QModelIndex) -> _NodeData:
    return cast(_ChildData, index.internalPointer())


def _raise_data_err(data: Any) -> NoReturn:
    raise RuntimeError(f'Graph viewmodel node has invalid data type {type(data)}')


def _checked(checked: bool) -> int:
    return int(Qt.Checked if checked else Qt.Unchecked)
