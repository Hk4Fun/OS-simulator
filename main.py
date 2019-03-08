import logging
import sys

from PyQt5.QtWidgets import QApplication

from simulator.settings import *

if __name__ == '__main__':
    levels = {'error': logging.ERROR,
              'warn': logging.WARN,
              'info': logging.INFO,
              'debug': logging.DEBUG}
    logger = logging.getLogger('log')
    logger.setLevel(levels[LOGGING_LEVEL])
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(ch)
    if SAVE_LOG_TO_FILE:
        fh = logging.FileHandler(LOG_FILE_PATH)
        fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(fh)

    app = QApplication(sys.argv)
    from simulator.mainwindow import ui_mainwindow

    ui_mainwindow.initFileUI()
    ui_mainwindow.show()
    exit(app.exec_())
