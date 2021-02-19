import logging
from dataclasses import dataclass
from typing import Any, List, NoReturn, Union, cast

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex
from PyQt5 import QtCore
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem

from .model import FilePlot

def mi_repr(self: QModelIndex) -> str:
    return f'Index({self.row()}, {self.column()}, {self.internalPointer()})'
QModelIndex.__repr__ = mi_repr

@dataclass
class _ChildData:
    """Internal data structure for child nodes (plots)"""
    parent: '_ParentData'
    plot: PlotDataItem

class _ParentData:
    """Internal data structure for parent nodes (files)"""
    def __init__(self, file_plot: FilePlot):
        self.path = file_plot.path
        self.children = [_ChildData(self, plot) for plot in file_plot.plots]

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, _ParentData):
            return False
        return self.path == o.path and self.children == o.children

_NodeData = Union[None, _ParentData, _ChildData]

def _get_data(index: QModelIndex) -> _NodeData:
    return  cast(_ChildData, index.internalPointer())

def _raise_data_err(data: Any) -> NoReturn:
    raise RuntimeError(f'Graph viewmodel node has invalid data type {type(data)}')

class GraphTreeModel(QAbstractItemModel):

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

        if role != Qt.DisplayRole:
            return None

        data = _get_data(index)
        if isinstance(data, _ParentData):
            return data.path.name
        elif isinstance(data, _ChildData):
            return data.plot.name()
        else:
            _raise_data_err(data)

    def headerData(self, section: int, orientation: Qt.Orientation,
            role: int) -> Any:
        # logging.debug('headerData(), section=%d, orientation=%d', section, orientation)
        if orientation != QtCore.Qt.Horizontal or role != QtCore.Qt.DisplayRole:
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
