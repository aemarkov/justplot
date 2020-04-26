#!/usr/bin/env python3

import sys
from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import numpy as np

class MainWindow(QtWidgets.QMainWindow):
    UI = 'ui/main.ui'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(self.UI, self)

        x = np.arange(0, 10, 0.01)
        y = np.sin(x)
        self.plotWidget.plot(x, y)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()