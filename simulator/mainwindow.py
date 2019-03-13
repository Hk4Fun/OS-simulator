from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QAbstractItemView, QHeaderView

from ui import mainwindow
from .errors import *
from .settings import *


class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)

        # Settings for right bar
        self.rightBarWidget.verticalHeader().setDefaultSectionSize(5)

        # Stretch last column of the table
        self.JobPoolTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.TerminatedTable.horizontalHeader().setStretchLastSection(True)
        self.ReadyTable.horizontalHeader().setStretchLastSection(True)
        self.SuspendTable.horizontalHeader().setStretchLastSection(True)

        # Connect slots
        self.StartButton.clicked.connect(self.slotStartButton)
        self.DaoshuBox.valueChanged.connect(self.slotMaxWaitingChanged)
        self.NewFile.clicked.connect(self.slotCreateNewFile)

    def initFileUI(self):
        file_chain.append('only C', 2, 'C 1 0\nC 1 1\nC 1 2\nC 1 3\nC 1 1\nQ 2')
        file_chain.append('c and K', 2, 'C 1 0\nK 4 1\nC 1 2\nQ 2')
        file_chain.append('C and k', 2, 'C 4 0\nK 1 1\nC 4 0\nQ 2')
        file_chain.append('all', 2, 'C 2 0\nR a 2 1\nC 2 2\nW a 2 15 3\nC 2 4\nQ 5')

        self.fileList.setRowCount(file_chain.length)
        self.fileList.setColumnCount(1)
        self.fileList.setHorizontalHeaderLabels(['文件名'])
        self.fileList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header = self.fileList.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        for i in range(0, file_chain.length):
            item = QTableWidgetItem(str(file_chain.fetch(i).name))
            self.fileList.setItem(i, 0, item)
            self.fileList.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.fileList.setSelectionMode(QAbstractItemView.SingleSelection)
        self.fileList.cellDoubleClicked.connect(self.editFile)

    def editFile(self, row, column):
        # integer
        self.ui_file = FileEditDialog(row)
        self.ui_file.exec()
        self.fileList.setRowCount(file_chain.length)
        self.fileList.setColumnCount(1)
        self.fileList.setHorizontalHeaderLabels(['文件名'])
        self.fileList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header = self.fileList.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        for i in range(0, file_chain.length):
            item = QTableWidgetItem(str(file_chain.fetch(i).name))
            self.fileList.setItem(i, 0, item)
            self.fileList.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.fileList.setSelectionMode(QAbstractItemView.SingleSelection)

    def closeEvent(self, *args, **kwargs):
        # terminate two scheduling threads before close mainWindow
        if hasattr(self, 'st') and hasattr(self, 'lt'):
            self.st.terminate()
            self.lt.terminate()
            self.st.wait()
            self.lt.wait()
        super().closeEvent(*args, **kwargs)

    def slotCreateNewFile(self):
        self.ui_file = FileEditDialog()
        if self.ui_file.exec():
            self.fileList.setRowCount(file_chain.length)
            self.fileList.setColumnCount(1)
            self.fileList.setHorizontalHeaderLabels(['文件名'])
            self.fileList.setEditTriggers(QAbstractItemView.NoEditTriggers)
            header = self.fileList.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            for i in range(0, file_chain.length):
                item = QTableWidgetItem(str(file_chain.fetch(i).name))
                self.fileList.setItem(i, 0, item)
                self.fileList.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.fileList.setSelectionMode(QAbstractItemView.SingleSelection)

    def slotStartButton(self):
        ready_pool.max = self.DaoshuBox.value()
        self.StartButton.setDisabled(True)
        self.StartButton.setText("正在运行")
        memory.allocate_for_os()
        # Create thread
        self.st = Shortterm(ready_pool)
        self.lt = Longterm(ready_pool, job_pool)

        # Start thread
        self.st.start()
        self.lt.start()

    def slotAddJobButton(self):
        job_pool.add(PCB(PCB.generate_pid(),
                         self.AddJobNameEdit.text(),
                         int(self.AddJobPriorityEdit.text()),
                         self.JobText.toPlainText()
                         ))

    def slotMaxWaitingChanged(self):
        ready_pool.max = self.DaoshuBox.value()

    # @QtCore.pyqtSlot(TableController, PCB, "QString")
    def slotTableRefresh(self, controller, process, operation):
        if operation == "append":
            controller.append(process)
        elif operation == "remove":
            controller.remove(process)
        elif operation == "io_complete":
            controller.edit(process.pid, 11, 'complete')

    # @QtCore.pyqtSlot(TableController, int, int, "QString")
    def slotTableEdit(self, controller, pid, column, new_text):
        controller.edit(pid, column, new_text)

    # @QtCore.pyqtSlot("QString", int)
    def slotMemoryTableEdit(self, operation, location):
        logger.info('{} {}'.format(operation, location))
        memory.table.item(location, 0).setBackground(
            COLOR_USED_MEMORY if operation == "allocate" else COLOR_MEMORY)

    # @QtCore.pyqtSlot("QString")
    def slotChangeRunningLabel(self, process_name):
        if process_name:
            self.NowRunningLabel.setText("Running: {}".format(process_name))
        else:
            self.NowRunningLabel.setText(" ")


ui_mainwindow = MainWindow()

from .file import FileEditDialog, file_chain
from .pcb import PCB
from .schedule import Shortterm, Longterm
from .pool import ready_pool, job_pool
from .memory import memory
