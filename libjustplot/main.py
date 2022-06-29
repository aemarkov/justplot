import sys
import argparse
from PyQt5 import QtWidgets
import logging

from .main_window import MainWindow


def main():
    configure_logger()
    parser = create_parser()
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('justplot')
    app.setOrganizationName('Markov')
    app.setOrganizationDomain('markov.org')
    window = MainWindow(args.files)
    window.show()
    app.exec()


def configure_logger():
    formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Simple graph plotter. Run without arguments to add files from GUI.')
    parser.add_argument('files', nargs='*', type=str, help='Files to plot')
    return parser
