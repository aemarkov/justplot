#!/usr/bin/env python3

import sys
from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import numpy as np
import pandas as pd

class MainWindow(QtWidgets.QMainWindow):
    UI = 'ui/main.ui'
    CSV_DELIMITER = ' '
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
        super().__init__(*args, **kwargs)
        uic.loadUi(self.UI, self)

        # Plot settings
        # self.plotWidget.getPlotItem().setAspectLocked(True)
        self.plotWidget.setBackground('w')
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.addLegend()
        self.color_index = 0

        self.data = {}

        self.btnAddPlot.clicked.connect(self.add_plot_slot)
        self.btnDeletePlot.clicked.connect(self.delete_plot_slot)

    def add_plot_slot(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', filter="CSV (*.csv *.DRIVEMAG)")[0]
        if fname != '':
            data = self.add_csv_data(fname)

    def delete_plot_slot(self):
        print('remove')

    def add_csv_data(self, fname: str) -> None:
        data = pd.read_csv(fname, sep=self.CSV_DELIMITER)
        self.plot_dataframe(data)
        self.data[fname] = data
        return data

    def plot_dataframe(self, data) -> None:
        x = data.iloc[:,0]
        xlabel = data.columns[0]
        for i in range(1, data.shape[1]):
            yi = data.iloc[:,i]
            label = data.columns[i]
            pen = pg.mkPen(color=self.next_color(), width=self.PEN_WIDTH)
            self.plotWidget.plot(x, yi, name=label, pen=pen)

    def next_color(self)->str:
        clr =  self.COLORS[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.COLORS)
        return clr

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
