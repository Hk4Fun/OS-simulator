import threading
import logging

from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore

from settings import *
from utils import mutex_lock
from mainwindow import ui_mainwindow
from pcb import PCB

logger = logging.getLogger('log')


class TableController:
    def __init__(self, table, content_each_line):
        self.table = table
        self.content_each_line = content_each_line
        self.table.itemDoubleClicked.connect(self.itemDoubleClickedSlot)
        self.lock = threading.Lock()
        self.last_running_line = -1

    @mutex_lock
    def append(self, process):
        """
        Append a row to table widget

        :param process: process to append to widget
        :return: none
        """
        self.table.setRowCount(self.table.rowCount() + 1)
        for j in range(0, len(self.content_each_line)):
            content = eval('process.' + self.content_each_line[j])
            if j == 3:
                # Special for priority column
                item = QTableWidgetItem('{:.2f}'.format(float(content)))
            elif j == 9:
                # for page fault rate
                item = QTableWidgetItem(
                    '{:.2f}%'.format(0 if process.references == 0 else process.page_faults / process.references * 100))
            else:
                item = QTableWidgetItem(str(content))
            self.table.setItem(self.table.rowCount() - 1, j, item)  # Add item to table
            self.table.scrollToItem(item)  # Scroll to item

    @mutex_lock
    def remove(self, process):
        """
        Remove a row in table widget

        :param process: process to remove from table widget
        :return: none
        """
        for i in range(0, self.table.rowCount()):
            if self.table.item(i, 0).text() == str(process.pid):
                # Move rows after me
                if i < self.table.rowCount() - 1:
                    for j in range(i, self.table.rowCount() - 1):
                        for k in range(0, len(self.content_each_line)):
                            self.table.setItem(j, k, QTableWidgetItem(self.table.item(j + 1, k).text()))
                break

        self.table.setRowCount(self.table.rowCount() - 1)  # row count - 1

    @mutex_lock
    def edit(self, process_id, column, new_text):
        """
        Edit a item and change its background color to yellow

        :param process_id: PID of process
        :param column: column to edit
        :param new_text: new text of QTableWidgetItem
        :return: none
        """

        for i in range(0, self.table.rowCount()):
            if self.table.item(i, 0).text() == str(process_id):
                if column == 3:  # for priority
                    new_text = '{:.2f}'.format(float(new_text))
                new_item = QTableWidgetItem(new_text)
                new_item.setBackground(QtGui.QColor(252, 222, 156))
                self.table.setItem(i, column, new_item)
                if new_text == 'running':
                    if self.last_running_line != -1 and self.last_running_line < self.table.rowCount():  # clear last running line
                        for j in range(self.table.columnCount()):
                            self.table.item(self.last_running_line, j).setBackground(QtGui.QColor(0, 0, 0, 0))
                    # pain new running line
                    for j in range(self.table.columnCount()):
                        self.table.item(i, j).setBackground(QtGui.QColor(0, 255, 255))
                    self.last_running_line = i

    def itemDoubleClickedSlot(self, item):
        """
        Slot for suspending and resuming process

        :param item: QTableWidgetItem clicked
        """
        if type(self).__name__ == 'ReadyTableController':
            if self.table.item(item.row(), 2).text() == "ready":
                logger.info("Suspend {}".format(self.table.item(item.row(), 0).text()))
                process = ready_pool.item(self.table.item(item.row(), 0).text())
                ready_pool.suspend(process)
                suspend_pool.add(process)
        elif type(self).__name__ == 'SuspendTableController':
            logger.info("Resume {}".format(self.table.item(item.row(), 0).text()))
            process = suspend_pool.item(self.table.item(item.row(), 0).text())
            suspend_pool.remove(process)
            ready_pool.resume(process)


class JobPoolTableController(TableController):
    pass


class ReadyTableController(TableController):
    pass


class SuspendTableController(TableController):
    pass


class TerminatedTableController(TableController):
    pass


class Pool(QtCore.QObject):
    refreshTableSignal = QtCore.pyqtSignal(TableController, PCB, "QString")
    editTableSignal = QtCore.pyqtSignal(TableController, int, int, "QString")
    running_label_change_signal = QtCore.pyqtSignal("QString")

    def __init__(self):
        super().__init__()
        self._pool = []
        self._idx = 0  # iterable
        self.lock = threading.Lock()
        self.connectSignal()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            job = self._pool[self._idx]
        except IndexError:
            self._idx = 0
            raise StopIteration()
        self._idx += 1
        return job

    def connectSignal(self):
        self.refreshTableSignal.connect(ui_mainwindow.slotTableRefresh)
        self.editTableSignal.connect(ui_mainwindow.slotTableEdit)
        self.running_label_change_signal.connect(ui_mainwindow.slotChangeRunningLabel)

    @mutex_lock
    def add(self, job):
        """
        Add a job to pool

        :param job: Job to add
        :return: none
        """
        self._pool.append(job)

        # Change job's status
        if type(self).__name__ == 'TerminatedPool':
            job.status = 'terminated'
        elif type(self).__name__ == 'ReadyPool':
            job.status = 'ready'
        elif type(self).__name__ == 'SuspendPool':
            job.status = 'suspend'

        self.refreshTableSignal.emit(self.table_controller, job, "append")  # Append to table widget

    @property
    def num(self):
        """
        Get number of items in pool

        :return: length of pool
        """
        return len(self._pool)

    def item(self, pid):
        """
        Get a item for specific PID

        :param pid: PID of item
        :return: An item of specified PID
        """
        for item in self._pool:
            if item.pid == int(pid):
                return item

    @mutex_lock
    def remove(self, identifier):
        """
        Remove a job
        :param identifier: job's pid or PCB
        :return: none
        """
        for each in self._pool:
            if isinstance(identifier, PCB):
                if each.pid == identifier.pid:
                    self._pool.remove(each)
                    self.refreshTableSignal.emit(self.table_controller, identifier, "remove")
                    return each
            elif isinstance(identifier, int):
                if each.pid == int(identifier):
                    self.refreshTableSignal.emit(self.table_controller, self.item(identifier), "remove")
                    self._pool.remove(each)
                    return each

    def __contains__(self, job):
        return job in self._pool


class JobPool(Pool):
    def __init__(self):
        super().__init__()
        table = ui_mainwindow.JobPoolTable
        content = ['pid',
                   'name',
                   'status',
                   'priority',
                   'required_memory']
        self.table_controller = JobPoolTableController(table=table, content_each_line=content)

    @mutex_lock
    def pop(self):
        """
        Get the first job and remove it from job pool: FCFS
        """
        if self._pool:
            job = self._pool.pop(0)
            self.refreshTableSignal.emit(self.table_controller, job, "remove")
            return job

    @mutex_lock
    def get(self):
        if self._pool:
            return self._pool[0]


class TerminatedPool(Pool):
    def __init__(self):
        super().__init__()
        table = ui_mainwindow.TerminatedTable
        content = ['pid', 'name']
        self.table_controller = TerminatedTableController(table=table, content_each_line=content)


class SuspendPool(Pool):
    def __init__(self):
        super().__init__()
        table = ui_mainwindow.SuspendTable
        content = ['pid',
                   'name',
                   'status',
                   'priority',
                   'required_memory',
                   'address',
                   'pc',
                   'references',
                   'page_faults',
                   'page_faults',
                   'io_type',
                   'io_status']
        self.table_controller = SuspendTableController(table=table, content_each_line=content)

    def remove(self, identifier):
        for each in self._pool:
            if isinstance(identifier, PCB):
                if each.pid == identifier.pid:
                    self._pool.remove(each)
                    self.refreshTableSignal.emit(self.table_controller, identifier, "io_complete")
                    io_pool.add(each)
                    return each


class ReadyPool(Pool):
    def __init__(self, max=5):
        super().__init__()
        table = ui_mainwindow.ReadyTable
        content = ['pid',
                   'name',
                   'status',
                   'priority',
                   'required_memory',
                   'address',
                   'pc',
                   'references',
                   'page_faults',
                   'page_faults']
        self.table_controller = ReadyTableController(table=table, content_each_line=content)
        self.scheduling_mode = MODE
        self.max = max
        self.suspended_count = 0

    def __repr__(self):
        return self.__str__()

    @mutex_lock
    def get(self):
        """
        Schedule a job for CPU to process

        :return: a job in pool
        """
        if self.scheduling_mode == 'priority':
            self._pool = sorted(self._pool, key=lambda item: item.priority)
        return self._pool[0]

    def after_time_slice(self, job):
        job.status = 'ready'
        self.editTableSignal.emit(self.table_controller, job.pid, 2, "ready")

    def change_priority(self, job):
        """
        Actively adjust job's priority: aging scheduling

        :param job: Job running this time
        :return: none
        """
        job.age = 0
        if job.priority < PRIORITY_MAX:
            job.priority += PRIORITY_ADD_EACH_TERN
        self.editTableSignal.emit(self.table_controller, job.pid, 3, str(job.priority))
        self.editTableSignal.emit(self.table_controller, job.pid, 2, "running")
        self.running_label_change_signal.emit(job.name)

        # Change other job's age
        for process in self._pool:
            if process.pid != job.pid:
                if process.age < len(AGING_TABLE) - 1:
                    process.age += 1
                if process.priority - AGING_TABLE[process.age] >= 0:
                    process.priority -= AGING_TABLE[process.age]
                    self.editTableSignal.emit(self.table_controller, process.pid, 3, str(process.priority))

    def suspend(self, job):
        """
        Suspend a process

        :param job: job to suspend
        :return: none
        """
        self.remove(job)
        self.suspended_count += 1

    def resume(self, job):
        """
        Resume a suspended job

        :param job: job to resume
        :return: none
        """
        self.add(job)
        self.suspended_count -= 1

    @property
    def count(self):
        """
        :return: number of jobs that could be scheduled
        """
        return self.max

    def slotChangePC(self, process):
        self.editTableSignal.emit(self.table_controller, process.pid, 6, str(process.pc))

    def slotChangePageRate(self, process):
        self.editTableSignal.emit(self.table_controller, process.pid, 7, str(process.references))
        self.editTableSignal.emit(self.table_controller, process.pid, 8, str(process.page_faults))
        self.editTableSignal.emit(self.table_controller, process.pid, 9,
                                  '{:.2f}%'.format(
                                      0 if process.references == 0 else process.page_faults / process.references * 100))


class IOCompletedPool:
    def __init__(self):
        self._pool = []

    def add(self, process):
        self._pool.append(process)

    def pop(self):
        return self._pool.pop(0)

    def __len__(self):
        return len(self._pool)


job_pool = JobPool()
ready_pool = ReadyPool()
terminated_pool = TerminatedPool()
suspend_pool = SuspendPool()
io_pool = IOCompletedPool()


