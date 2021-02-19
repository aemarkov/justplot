import os
import logging
from typing import Optional, Sequence
from pathlib import Path

import numpy as np
import pandas as pd
import pandas.errors

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem

from .exception import PlotError
from .tree_model import PlotTreeModel, PlotVisibleChanged
from .model import FilePlot

class MainWindow(QMainWindow):
    UI = os.path.join(os.path.dirname(__file__), 'ui/main.ui')
    CSV_DELIMITER: Optional[str] = None
    # Matplotlib default property cycle
    COLORS = [
        '#1f77b4',
        '#ff7f0e',
        '#2ca02c',
        '#d62728',
        '#9467bd',
        '#8c564b',
        '#e377c2',
        '#7f7f7f',
        '#bcbd22',
        '#17becf']
    PEN_WIDTH=2

    def __init__(self, *args, **kwargs):
        logging.info('MainWindow initialization')
        super().__init__(*args, **kwargs)
        uic.loadUi(self.UI, self)

        # Plot settings
        # self.plotWidget.getPlotItem().setAspectLocked(True)
        self.plotWidget.setBackground('w')
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.addLegend()
        self.color_index = 0

        self.btnAddPlot.clicked.connect(self.add_plot_slot)
        self.btnDeletePlot.clicked.connect(self.delete_plot_slot)

        self.model = PlotTreeModel()
        self.model.plot_visible_changed.connect(self.plot_visible_changed_slot)
        self.treeView.setModel(self.model)

    def add_plot_slot(self):
        logging.info('Show open log file dialog')
        try:
            fname = QFileDialog.getOpenFileName(self, 'Open file', filter="CSV (*.*)")[0]
            if fname != '':
                self.add_csv_data(Path(fname))
        except PlotError as e:
            self.show_dialog('Failed to plot data from file: {}'.format(str(e)),
                icon=QMessageBox.Warning)
        except pandas.errors.ParserError as e:
            logging.error('Pandas parsing error: %s', e)
            self.show_dialog('Failed to plot data from file: unable to parse file',
                details=str(e), icon=QMessageBox.Warning)

    def delete_plot_slot(self):
        print('remove')

    def plot_visible_changed_slot(self, arg: PlotVisibleChanged):
        # TODO: Maybe it is better to use Model/View approach
        if arg.is_visible:
            logging.info('Hide plot %s', arg.plot.name())
            self.plotWidget.addItem(arg.plot)
        else:
            logging.info('Show plot %s', arg.plot.name())
            self.plotWidget.removeItem(arg.plot)

    def add_csv_data(self, path: Path):
        logging.info('Loading file %s', path)

        if self.CSV_DELIMITER is None:
            logging.debug('Delimeter: any whitespace')
            data =  pd.read_csv(path, delim_whitespace=True)
        else:
            logging.debug('Delimeter: "%s"', self.CSV_DELIMITER)
            data =  pd.read_csv(path, sep=self.CSV_DELIMITER)

        plots = self.plot_dataframe(data)
        self.model.add_file(FilePlot(path, plots))

    def plot_dataframe(self, data: pd.DataFrame) -> Sequence[PlotDataItem]:
        x = data.iloc[:,0]
        nrows, ncols = data.shape
        logging.debug('Table size: columns=%d, rows=%d', ncols, nrows)
        if ncols < 2:
            err = 'Table should contain at least two columns (X, Y) to be plotted'
            logging.error(err)
            raise PlotError(err)

        x_label = data.columns[0]

        plots = []
        for i in range(1, data.shape[1]):
            yi = data.iloc[:,i]
            label = f'{data.columns[i]}({x_label})'
            pen = pg.mkPen(color=self.next_color(), width=self.PEN_WIDTH)
            item = self.plotWidget.plot(x, yi, name=label, pen=pen)
            plots.append(item)
        return plots

    def next_color(self)->str:
        clr =  self.COLORS[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.COLORS)
        return clr

    def show_dialog(self, text: str, details: str = None, icon: QMessageBox.Icon = QMessageBox.Information):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setWindowTitle('JustPlot')
        msg.setText(text)
        if details is not None:
            msg.setDetailedText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
