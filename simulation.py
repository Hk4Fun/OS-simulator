import sys
import random
import time
import threading
import functools
import logging
from abc import ABCMeta, abstractmethod

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import QtCore, QtGui

import mainwindow
import name_generator
from settings import *

COLOR_MEMORY = QtGui.QColor(*COLOR_MEMORY)
COLOR_USED_MEMORY = QtGui.QColor(*COLOR_USED_MEMORY)


def mutex_lock(func):
    """
    Mutex lock decorator for pools

    :param fun: function to decorate
    :return: wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args):
        self = args[0]
        self.lock.acquire()
        value = func(*args)
        self.lock.release()
        return value

    return wrapper


class PCB:
    def __init__(self, pid, name="process", priority=1, required_time=200):
        self.pid = pid
        self.name = name if name else "process"
        self.priority = priority if priority else 1
        self.required_time = required_time if required_time else 200
        self.status = 'new'
        self.address = hex(id(self))
        self.age = 0
        self.required_memory = random.randint(1, 10)
        self.allocated_memory_start = None

    def __str__(self):
        print("<PCB {0} {2}[{1}]> priority:".format(str(self.pid),
                                                    str(self.status),
                                                    self.name), end='')
        print("{0}".format(str(self.priority)), end='')
        print(" need_time:{0} address:{1}".format(str(self.required_time), self.address), end='')
        return ''

    def __repr__(self):
        return "<PCB {0} {3}[{1}]> priority:{2} need_time:{4}".format(str(self.pid),
                                                                      str(self.status),
                                                                      str(self.priority),
                                                                      self.name,
                                                                      str(self.required_time))

    @staticmethod
    def random():
        """
        Generate a random job

        :return: a random job object
        """
        pid = PCB.generate_pid()
        name = name_generator.gen_one_word_digit(lowercase=False)
        priority = random.randint(1, 7)
        required_time = random.randint(200, 1000)
        used_PIDs.add(pid)
        return PCB(pid, name, priority, required_time)

    @staticmethod
    def generate_pid():
        """
        Generate a random PID number

        :return: an unique int number
        """
        pid = random.randint(1, 10000)
        # Avoid duplicated PID
        while pid in used_PIDs:
            pid = random.randint(1, 10000)
        return pid


class Frame:
    pass

class PageTable:
    pass


class TableController:
    def __init__(self, table, content_each_line):
        self.table = table
        self.content_each_line = content_each_line
        self.table.itemDoubleClicked.connect(self.itemDoubleClickedSlot)
        self.lock = threading.Lock()

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
                item = QTableWidgetItem(str('{:.2f}'.format(float(content))))
            elif j == 7:
                item = QTableWidgetItem(str(hex(content)))
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
                if column == 3:
                    new_text = '{:.2f}'.format(float(new_text))
                new_item = QTableWidgetItem(new_text)
                new_item.setBackground(QtGui.QColor(252, 222, 156))
                self.table.setItem(i, column, new_item)
                if new_text == 'running':
                    for j in range(self.table.columnCount()):
                        self.table.item(i, j).setBackground(QtGui.QColor(0, 255, 255))

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
        self.lock = threading.Lock()
        self.connectSignal()

    def __str__(self):
        print("<{1} Pool ({0})>".format(len(self._pool), type(self).__name__))
        for job in self._pool:
            print(job)
        print('')
        return ""

    def __repr__(self):
        return "<PCB Pool ({0})>:{1}".format(len(self._pool), [job for job in self._pool])

    def connectSignal(self):
        self.refreshTableSignal.connect(UI_main_window.slotTableRefresh)
        self.editTableSignal.connect(UI_main_window.slotTableEdit)
        self.running_label_change_signal.connect(UI_main_window.slotChangeRunningLabel)

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
                    self.refreshTableSignal.emit(self.table_controller, identifier, "remove")
                    self._pool.remove(each)
                    return each
            elif isinstance(identifier, int):
                if each.pid == int(identifier):
                    self.refreshTableSignal.emit(self.table_controller, self.item(identifier), "remove")
                    self._pool.remove(each)
                    return each


class JobPool(Pool):
    def __init__(self):
        super().__init__()
        table = UI_main_window.JobPoolTable
        content = ['pid',
                   'name',
                   'status',
                   'priority',
                   'required_time',
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
        table = UI_main_window.TerminatedTable
        content = ['pid', 'name']
        self.table_controller = TerminatedTableController(table=table, content_each_line=content)


class SuspendPool(Pool):
    def __init__(self):
        super().__init__()
        table = UI_main_window.SuspendTable
        content = ['pid',
                   'name',
                   'status',
                   'priority',
                   'required_time',
                   'required_memory',
                   'address',
                   'allocated_memory_start']
        self.table_controller = SuspendTableController(table=table, content_each_line=content)


class ReadyPool(Pool):
    def __init__(self, scheduling_mode='priority', max=5):
        super().__init__()
        table = UI_main_window.ReadyTable
        content = ['pid',
                   'name',
                   'status',
                   'priority',
                   'required_time',
                   'required_memory',
                   'address',
                   'allocated_memory_start']
        self.table_controller = ReadyTableController(table=table, content_each_line=content)
        self.scheduling_mode = scheduling_mode
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

    def minus_time(self, job):
        """
        Minus a job's required_time and sync to table widget

        :param job: A job to minus its time
        :return: none
        """
        job.status = 'ready'
        if job.required_time >= SUB_TIME:
            job.required_time -= SUB_TIME
        else:
            job.required_time = 0

        # Update table widget
        self.editTableSignal.emit(self.table_controller, job.pid, 4, str(job.required_time))
        self.editTableSignal.emit(self.table_controller, job.pid, 2, "ready")

        # Need to be terminated
        if job.required_time == 0:
            logger.info('{0} terminated'.format(job.name))
            self.remove(job.pid)  # remove job from waiting list
            memory.free(job.required_memory, job.allocated_memory_start)  # free memory
            terminated_pool.add(job)  # add to terminated pool
            if len(self._pool) == 0:
                self.running_label_change_signal.emit("")

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
        return self.max - self.suspended_count


class Memory(QtCore.QObject):
    memory_edit_signal = QtCore.pyqtSignal("QString", int)

    class mem:
        __slots__ = ('start', 'length')

        def __init__(self, start, length):
            self.start = start
            self.length = length

    def __init__(self, table):
        super().__init__()
        self.table = table
        self.lock = threading.Lock()
        self.free_mem = [self.mem(0, TOTAL_MEM)]
        self.memory_edit_signal.connect(UI_main_window.slotMemoryTableEdit)
        self._used = 0

        # Init table widget
        for i in range(0, TOTAL_MEM):
            self.table.setRowCount(self.table.rowCount() + 1)
            item = QTableWidgetItem(" ")
            item.setBackground(COLOR_MEMORY)
            self.table.setItem(self.table.rowCount() - 1, 0, item)

    def filling(self, free_mem, mem_need):
        for each_location in range(free_mem.start, free_mem.start + mem_need):
            self._edit_table_widget("allocate", each_location)

    def unfilling(self, mem_start, mem_length):
        for each_location in range(mem_start, mem_start + mem_length):
            self._edit_table_widget("free", each_location)

    @mutex_lock
    def allocate(self, mem_need):
        """
        Allocate memory for a process: use First Fit algorithm

        :return: Starting address or None
        """
        for each_free_mem in self.free_mem:
            if each_free_mem.length >= mem_need:
                # change color
                self.filling(each_free_mem, mem_need)
                each_free_mem.length -= mem_need
                each_free_mem.start += mem_need
                if each_free_mem.length == 0:
                    self.free_mem.remove(each_free_mem)
                self._used += mem_need
                return each_free_mem.start - mem_need

    @mutex_lock
    def free(self, mem_length, mem_start):
        """
        Free memory for a process

        :return: None
        """
        self.unfilling(mem_start, mem_length)
        self._used -= mem_length
        self.free_mem.append(self.mem(mem_start, mem_length))
        # merge intervals
        self.free_mem.sort(key=lambda item: item.start)
        i = 0
        while True:
            cur = self.free_mem[i]
            if i + 1 < len(self.free_mem):
                next = self.free_mem[i + 1]
            else:
                break
            if cur.start + cur.length == next.start:
                cur.length += next.length
                self.free_mem.remove(next)
            else:
                i += 1

    @property
    def used(self):
        return self._used

    def _edit_table_widget(self, operation, location):
        self.memory_edit_signal.emit(operation, location)


class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)

        # Settings for right bar
        self.rightBarWidget.verticalHeader().setDefaultSectionSize(5)

        # Stretch last column of the table
        self.TerminatedTable.horizontalHeader().setStretchLastSection(True)
        self.ReadyTable.horizontalHeader().setStretchLastSection(True)
        self.SuspendTable.horizontalHeader().setStretchLastSection(True)

        # Connect slots
        self.StartButton.clicked.connect(self.slotStartButton)
        self.GenerateJobButton.clicked.connect(self.slotGenerateJobButton)
        self.AddJobButton.clicked.connect(self.slotAddJobButton)
        self.DaoshuBox.valueChanged.connect(self.slotMaxWaitingChanged)

    def closeEvent(self, *args, **kwargs):
        # terminate two scheduling threads before close mainWindow
        if hasattr(self, 'st') and hasattr(self, 'lt'):
            self.st.terminate()
            self.lt.terminate()
            self.st_scheduling_thread.join()
            self.lt_scheduling_thread.join()
        super().closeEvent(*args, **kwargs)

    def slotStartButton(self):
        ready_pool.max = self.DaoshuBox.value()
        self.StartButton.setDisabled(True)
        self.StartButton.setText("正在运行")

        # Create thread
        self.st = Shortterm()
        self.lt = Longterm()
        self.st_scheduling_thread = threading.Thread(target=self.st.run,
                                                     args=(MODE, ready_pool))
        self.lt_scheduling_thread = threading.Thread(target=self.lt.run,
                                                     args=(MODE, ready_pool, job_pool))

        memory.allocate(MEM_OS_TAKE)

        # Start thread
        self.st_scheduling_thread.start()
        self.lt_scheduling_thread.start()

    def slotGenerateJobButton(self):
        for i in range(self.RandomCountBox.value()):
            random_process = PCB.random()
            job_pool.add(random_process)

    def slotAddJobButton(self):
        job_pool.add(PCB(PCB.generate_pid(),
                         self.AddJobNameEdit.text(),
                         int(self.AddJobPriorityEdit.text()),
                         int(self.AddJobTimeEdit.text())
                         ))

    def slotMaxWaitingChanged(self):
        ready_pool.max = self.DaoshuBox.value()

    @QtCore.pyqtSlot(TableController, PCB, "QString")
    def slotTableRefresh(self, controller, process, operation):
        if operation == "append":
            controller.append(process)
        elif operation == "remove":
            controller.remove(process)

    @QtCore.pyqtSlot(TableController, int, int, "QString")
    def slotTableEdit(self, controller, pid, column, new_text):
        controller.edit(pid, column, new_text)

    @QtCore.pyqtSlot("QString", int)
    def slotMemoryTableEdit(self, operation, location):
        logger.info('{} {}'.format(operation, location))
        memory.table.item(location, 0).setBackground(
            COLOR_USED_MEMORY if operation == "allocate" else COLOR_MEMORY)

    @QtCore.pyqtSlot("QString")
    def slotChangeRunningLabel(self, process_name):
        if process_name:
            self.NowRunningLabel.setText("Running: {}".format(process_name))
        else:
            self.NowRunningLabel.setText(" ")


class SchedulingThread(metaclass=ABCMeta):
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    @abstractmethod
    def run(self, *args):
        pass


class Shortterm(SchedulingThread):

    def refreshStatus(self):
        UI_main_window.label_job.setText(str(job_pool.num))
        UI_main_window.label_ready.setText(str(ready_pool.num))
        UI_main_window.label_suspended.setText(str(suspend_pool.num))
        UI_main_window.label_terminated.setText(str(terminated_pool.num))
        UI_main_window.label_memory.setText('{:.2f}% ({}/{})'.format(memory.used / TOTAL_MEM, memory.used, TOTAL_MEM))

    def run(self, mode, ready_pl):
        """
        Thread for CPU scheduling

        :param mode: Scheduling mode
        :param ready_pl: ready pool
        """
        while self._running:
            if ready_pl.num > 0:
                processing_job = ready_pl.get()
                processing_job.status = 'running'
                if mode == 'priority':
                    logger.info('Running {0}...'.format(processing_job.name))
                    ready_pl.change_priority(processing_job)
                    self.refreshStatus()
                    time.sleep(CPU_PROCESS_TIME)  # Sleep just for show
                    ready_pl.minus_time(processing_job)
            time.sleep(0.001)


class Longterm(SchedulingThread):
    def run(self, mode, ready_pl, job_pl):
        """
        # Thread for long term scheduling

        :param mode: mode for scheduling
        :param ready_pl: ready pool object
        :param job_pl: job pool object
        """
        while self._running:
            if ready_pl.num < ready_pl.count:
                job = job_pl.pop()
                if job:
                    mem = memory.allocate(job.required_memory)
                    if mem is None:
                        job_pl.add(job)
                    else:
                        ready_pl.add(job)
                        job.allocated_memory_start = mem
            time.sleep(0.001)


def setLog():
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
    return logger


if __name__ == '__main__':
    app = QApplication(sys.argv)
    UI_main_window = MainWindow()

    logger = setLog()
    used_PIDs = set()

    # Create pool instances and memory
    job_pool = JobPool()
    ready_pool = ReadyPool(scheduling_mode=MODE, max=5)
    terminated_pool = TerminatedPool()
    suspend_pool = SuspendPool()
    memory = Memory(UI_main_window.rightBarWidget)

    # Show main window
    UI_main_window.show()
    exit(app.exec_())
