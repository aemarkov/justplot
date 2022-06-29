import os
import logging
from typing import Optional, Sequence
from pathlib import Path

import pandas as pd
from pandas.core.frame import DataFrame
import pandas.errors

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtCore import QItemSelectionModel, QSettings
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem

from .exception import PlotError
from .tree_model import PlotTreeModel, PlotVisibleChanged
from .model import FilePlot
from .color_picker import ColorPicker

OPEN_DIR_KEY = 'open_dir'

class MainWindow(QMainWindow):

    plotWidget: PlotWidget
    selection: QItemSelectionModel

    UI = os.path.join(os.path.dirname(__file__), 'ui/main.ui')
    CSV_DELIMITER: Optional[str] = None
    PEN_WIDTH = 2

    def __init__(self, default_files: Sequence[str] = [], *args, **kwargs):
        logging.info('MainWindow initialization')
        super().__init__(*args, **kwargs)
        uic.loadUi(self.UI, self)
        self.showMaximized()

        # Plot settings
        # self.plotWidget.getPlotItem().setAspectLocked(True)
        self.plotWidget.setBackground('w')
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.addLegend()

        self.btnAddPlot.clicked.connect(self.add_plot_slot)
        self.btnDeletePlot.clicked.connect(self.delete_plot_slot)
        self.btnDeleteall.clicked.connect(self.delete_all_slot)

        self._color = ColorPicker()

        self.model = PlotTreeModel()
        self.treeView.setModel(self.model)
        self.selection = self.treeView.selectionModel()
        self.model.plot_visible_changed.connect(self.plot_visible_changed_slot)
        self.model.plot_cleared.connect(self.plot_cleared_slot)

        for file in default_files:
            self._load_and_plot_file(file)

    # --- slots ----------------------------------------------------------------

    def add_plot_slot(self):
        logging.info('Show open log file dialog')

        # Restore last directory
        settings = QSettings()
        open_dir = settings.value(OPEN_DIR_KEY)
        logging.debug('Restore open directory: %s', open_dir)

        files = QFileDialog.getOpenFileNames(self, 'Open file', open_dir,
            filter="CSV (*.*)")[0]

        # Store last directory
        if len(files) > 0:
            directory = os.path.dirname(files[0])
            settings.setValue(OPEN_DIR_KEY, directory)


        for file in files:
            self._load_and_plot_file(file)

    def delete_plot_slot(self):
        self.model.delete_plot(self.selection.currentIndex())

    def delete_all_slot(self):
        self.model.delete_all()

    def plot_visible_changed_slot(self, arg: PlotVisibleChanged):
        # TODO: Maybe it is better to use Model/View approach
        if arg.is_visible:
            logging.info('Add plot %s', arg.plot.name())
            self.plotWidget.addItem(arg.plot)
        else:
            logging.info('Delete plot %s', arg.plot.name())
            self.plotWidget.removeItem(arg.plot)

    def plot_cleared_slot(self):
        self.plotWidget.clear()

    # --- private --------------------------------------------------------------

    def _load_and_plot_file(self, path: str):
        try:
            _path = Path(path)
            data = self._load_csv_file(_path)
            plots = self._plot_dataframe(data)
            self.model.add_file(FilePlot(_path, plots))
        except FileNotFoundError as e:
            msg = 'Unable to open file: {}'.format(str(e))
            logging.error(msg)
            self._show_dialog(msg, icon=QMessageBox.Warning)
        except PlotError as e:
            msg = 'Failed to plot data from file: {}'.format(str(e))
            logging.error(msg)
            self._show_dialog(msg, icon=QMessageBox.Warning)
        except pandas.errors.ParserError as e:
            logging.error('Pandas parsing error: %s', e)
            self._show_dialog('Failed to plot data from file: unable to parse file',
                details=str(e), icon=QMessageBox.Warning)

    def _load_csv_file(self, path: Path) -> DataFrame:
        logging.info('Loading file %s', path)

        if self.CSV_DELIMITER is None:
            logging.debug('Delimeter: any whitespace')
            return pd.read_csv(path, delim_whitespace=True)
        else:
            logging.debug('Delimeter: "%s"', self.CSV_DELIMITER)
            return pd.read_csv(path, sep=self.CSV_DELIMITER)

    def _plot_dataframe(self, data: pd.DataFrame) -> Sequence[PlotDataItem]:
        x = data.iloc[:, 0]
        nrows, ncols = data.shape
        logging.debug('Table size: columns=%d, rows=%d', ncols, nrows)
        if ncols < 2:
            err = 'Table should contain at least two columns (X, Y) to be plotted'
            logging.error(err)
            raise PlotError(err)

        x_label = data.columns[0]

        plots = []
        for i in range(1, data.shape[1]):
            yi = data.iloc[:, i]
            label = f'{data.columns[i]}({x_label})'
            pen = pg.mkPen(color=self._color.next_color(), width=self.PEN_WIDTH)
            item = self.plotWidget.plot(x, yi, name=label, pen=pen)
            plots.append(item)
        return plots

    def _show_dialog(self, text: str, details: str = None,
            icon: QMessageBox.Icon = QMessageBox.Information):

        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setWindowTitle('JustPlot')
        msg.setText(text)
        if details is not None:
            msg.setDetailedText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
