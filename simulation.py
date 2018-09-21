import sys
import random
import time
import threading
import functools
import logging
from collections import namedtuple
from abc import ABCMeta, abstractmethod

from PyQt5.QtWidgets import (QMessageBox, QApplication, QMainWindow, QTableWidgetItem,
                             QAbstractItemView, QHeaderView, QDialog)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QThread, QTimer

import file_edit
import mainwindow
from settings import *
from interpreter import Intr_table

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


class OutOfMemoryError(Exception):
    def __init__(self):
        super().__init__()
        logger.error('out of memory!')


class CodeFormatError(Exception):
    def __init__(self):
        super().__init__()
        logger.error('code format error!')


class Code(metaclass=ABCMeta):
    def __init__(self, *args, process):
        self.process = process

    @abstractmethod
    def exec(self, *args):
        pass

    def sub_time(self):
        self.remain_time -= CPU_PROCESS_TIME
        if self.remain_time < 0:
            self.remain_time = 0
            self.process.pc += 1


class C(Code):
    def __init__(self, exectime, process):
        super().__init__(process=process)
        self.exectime = int(exectime)
        self.remain_time = self.exectime

    def exec(self, *args):
        logger.info('exec code C, remain_time: {}'.format(self.remain_time))
        self.sub_time()


class Q(Code):
    def exec(self):
        logger.info('{0} terminated'.format(self.process.name))
        ready_pool.remove(self.process.pid)  # remove job from waiting list
        memory.free(self.process)  # free memory
        terminated_pool.add(self.process)  # add to terminated pool
        if len(ready_pool._pool) == 0:
            ready_pool.running_label_change_signal.emit("")


class TimerThread(QThread):
    def __init__(self, process, exectime):
        super().__init__()
        self.process = process
        self.exectime = exectime

    def fromSuspend2Ready(self):
        logger.info("Resume {}".format(self.process.name))
        self.process.io_status = 'complete'
        suspend_pool.remove(self.process)
        self.process.pc += 1

    def run(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fromSuspend2Ready)
        self.timer.start(self.exectime * 1000)
        self.exec_()


class IO(Code):
    def __init__(self, exectime, process):
        super().__init__(process=process)
        self.exectime = int(exectime)
        self.timerThread = TimerThread(self.process, self.exectime)

    def change_io_type(self):
        raise NotImplementedError

    def exec(self):
        logger.info('exec code K, exectime: {}'.format(self.exectime))
        self.change_io_type()
        self.process.io_status = 'running'
        self.fromReady2Suspend()
        self.timerThread.start()

    def fromReady2Suspend(self):
        logger.info("Suspend {}".format(self.process.name))
        ready_pool.suspend(self.process)
        suspend_pool.add(self.process)


class K(IO):
    def change_io_type(self):
        self.process.io_type = 'keyboard'


class P(IO):
    def change_io_type(self):
        self.process.io_type = 'printer'


class R(IO):
    def __init__(self, filename, exectime, process):
        super().__init__(exectime, process)
        self.filename = filename

    def change_io_type(self):
        self.process.io_type = 'read file'


class W(IO):
    def __init__(self, filename, exectime, size, process):
        super().__init__(exectime, process)
        self.filename = filename
        self.size = size

    def change_io_type(self):
        self.process.io_type = 'write file'


instructions = {'C': C,
                'K': K,
                'P': P,
                'R': R,
                'W': W,
                'Q': Q}


class PTE:
    __slots__ = ['frame', 'recent_access_time', 'valid_bit']

    def __init__(self, frame, recent_access_time, valid_bit):
        self.frame = frame
        self.recent_access_time = recent_access_time
        self.valid_bit = valid_bit


class PCB:
    def __init__(self, pid, name=None, priority=4, codes=''):
        self.pid = pid
        self.name = name if name else "P{}".format(pid)
        self.priority = priority
        self.status = 'new'
        self.address = hex(id(self))
        self.age = 0
        self.pc = 0
        self.codes = self.translate(codes)
        self.page_table = {}
        self.references = 0
        self.page_faults = 0
        self.code_exec_status = None  # new, running, stopped
        self.io_type = None
        self.io_status = None

    def translate(self, codes):
        lines = codes.split('\n')
        if lines[-1][0] != 'Q':
            raise CodeFormatError()
        res = []
        page_nums = []

        try:
            for line in lines:
                *code, page_num = line.split(' ')
                res.append((instructions[code[0]](*code[1:], process=self), page_num))
                page_nums.append(page_num)
        except Exception:
            raise CodeFormatError()

        self.calcMemory(page_nums)
        return res

    def calcMemory(self, page_nums):
        self.required_memory = len(set(page_nums))

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

    def exec_next_code(self):
        code, page_num = self.codes[self.pc]
        ready_pool.slotChangePC(self)
        try:
            memory.access(self, page_num)
        except OutOfMemoryError:
            logger.info('{0} terminated'.format(self.name))
            ready_pool.remove(self.pid)  # remove job from waiting list
            terminated_pool.add(self)  # add to terminated pool
            if len(ready_pool._pool) == 0:
                ready_pool.running_label_change_signal.emit("")
            raise
        ready_pool.slotChangePageRate(self)
        code.exec()


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
        table = UI_main_window.JobPoolTable
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
    def __init__(self, scheduling_mode='priority', max=5):
        super().__init__()
        table = UI_main_window.ReadyTable
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


class Memory(QtCore.QObject):
    memory_edit_signal = QtCore.pyqtSignal("QString", int)

    def __init__(self, table):
        super().__init__()
        self.table = table
        self.lock = threading.Lock()
        self.free_frames = list(range(TOTAL_MEM))
        self.memory_edit_signal.connect(UI_main_window.slotMemoryTableEdit)
        self.references = 0
        self.page_faults = 0
        self.init_memory_bar()

    def init_memory_bar(self):
        for i in range(0, TOTAL_MEM):
            self.table.setRowCount(self.table.rowCount() + 1)
            item = QTableWidgetItem(" ")
            item.setBackground(COLOR_MEMORY)
            self.table.setItem(self.table.rowCount() - 1, 0, item)

    def already_in_memory(self, process, page_num):
        return page_num in process.page_table and process.page_table[page_num].valid_bit

    @mutex_lock
    def access(self, process, page_num):
        process.references += 1
        self.references += 1
        if self.already_in_memory(process, page_num):
            # update the reference time
            process.page_table[page_num].recent_access_time = time.time()
            frame = process.page_table[page_num].frame
            logger.info(
                "{} requests page {}. This page is already in memory frame {}".format(process.name, page_num, frame))
        else:
            # PAGE FAULT!!!!
            self.page_faults += 1
            process.page_faults += 1
            free_frame = self.get_frame()
            self._edit_table_widget("allocate", free_frame)
            process.page_table[page_num] = PTE(free_frame, time.time(), True)
            logger.info(
                "{} requests page {}. Page Fault occurred. Frame {} granted".format(process.name, page_num, free_frame))

    def get_frame(self):
        if len(self.free_frames) != 0:
            return self.free_frames.pop(0)
        else:
            # we have to boot lru add frame to free list, and return it
            self.replace_by_lru()
            return self.free_frames.pop(0)

    def replace_by_lru(self):
        frames_in_memory = []
        item = namedtuple('item', ['process', 'page_num', 'pte'])
        for process in ready_pool:
            for page_num, pte in process.page_table.items():
                if pte.valid_bit:
                    frames_in_memory.append(item(process, page_num, pte))
        # find the oldest / lru of the frames in memory
        try:
            lru = frames_in_memory[0]
        except IndexError:
            self.lock.release()
            raise OutOfMemoryError()
        for item in frames_in_memory:
            if item.pte.recent_access_time < lru.pte.recent_access_time:
                lru = item
        # remove lru frame from physical memory
        self._edit_table_widget("free", lru.pte.frame)
        # remove lru page from process's page table
        lru.process.page_table.pop(lru.page_num)
        # add free frame to free list
        self.free_frames.append(lru.pte.frame)
        # set the valid bit of the removed page to False
        lru.pte.valid_bit = False
        logger.info('lru occurred: frame {} out'.format(lru.pte.frame))

    @mutex_lock
    def free(self, process):
        for pte in process.page_table.values():
            self.free_frames.append(pte.frame)
            self._edit_table_widget('free', pte.frame)

    @property
    def used(self):
        return TOTAL_MEM - len(self.free_frames)

    def _edit_table_widget(self, operation, location):
        self.memory_edit_signal.emit(operation, location)

    def allocate_for_os(self):
        for i in range(MEM_OS_TAKE):
            self.free_frames.pop(0)
            self._edit_table_widget('allocate', i)


class Node:
    def __init__(self, name=None, prio=None, code=None):
        self.name = name
        self.prio = prio
        self.code = code
        self._next = None


class Chain:
    def __init__(self):
        self._head = None
        self.length = 0

    def isEmpty(self):
        return self.length == 0

    def append(self, name, prio, code):
        node = Node(name, prio, code)
        if self._head == None:
            self._head = node
        else:
            be_node = self._head
            while be_node._next:
                be_node = be_node._next
            be_node._next = node
        self.length += 1

    def insert(self, index, item):
        if self.isEmpty():
            return
        if index < 0 or index >= self.length:
            return
        in_node = Node(item)
        node = self._head
        count = 1
        while True:
            node = node._next
            count += 1
            if count == index:
                next_node = node._next
                node._next = in_node
                in_node._next = next_node
                self.length += 1
                return

    def delete(self, name):
        if self.isEmpty():
            return
        else:
            node = self._head
            if (node.name == name):
                self._head = self._head._next
                self.length -= 1
                return
            while node._next != None:
                if name == node._next.name:
                    node._next = node._next._next
                    self.length -= 1
                    return
                node = node._next

    def fetch(self, index):
        if self.isEmpty():
            return
        if index < 0 or index >= self.length:
            return
        else:
            node = self._head
            count = 0
            while node is not None:
                if index == count:
                    return node
                node = node._next
                count += 1


class FileEditDialog(QDialog, file_edit.Ui_Dialog):
    def __init__(self, fileId=None, parent=None):
        super().__init__()
        self.setupUi(self)
        self.saveFileButton.clicked.connect(self.save)
        self.deleteFileButton.clicked.connect(self.delete)
        self.addJobButton.clicked.connect(self.addJob)
        self.isOld = 0

        if fileId != None:
            self.AddJobPriorityEdit_2.setText(file_chain.fetch(fileId).name)
            self.AddJobNameEdit_2.setText(str(file_chain.fetch(fileId).prio))
            self.JobText.setText(file_chain.fetch(fileId).code)
            self.isOld = 1
        self.name = self.AddJobPriorityEdit_2.text()

    def addJob(self):
        if self.JobText.toPlainText() == '':
            msg = '代码不能为空！'
            QMessageBox().critical(self, '代码出错', msg, QMessageBox.Yes, QMessageBox.Yes)
            return
        try:
            job_pool.add(PCB(PCB.generate_pid(),
                             self.AddJobPriorityEdit_2.text(),
                             int(self.AddJobNameEdit_2.text()),
                             self.JobText.toPlainText()
                             ))
        except CodeFormatError:
            msg = '代码格式出错！'
            QMessageBox().critical(self, '代码出错', msg, QMessageBox.Yes, QMessageBox.Yes)
        self.accept()

    def save(self):
        if (self.isOld == 0):
            self.name = self.AddJobPriorityEdit_2.text()
        file_chain.delete(self.name)
        file_chain.append(self.AddJobPriorityEdit_2.text(), int(self.AddJobNameEdit_2.text()),
                          self.JobText.toPlainText())
        msg = '保存成功！'
        QMessageBox().information(self, '保存成功', msg, QMessageBox.Yes, QMessageBox.Yes)
        self.accept()

    def delete(self):
        if (self.isOld == 0):
            self.name = self.AddJobPriorityEdit_2.text()
        file_chain.delete(self.name)
        self.accept()


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
        self.DaoshuBox.valueChanged.connect(self.slotMaxWaitingChanged)
        self.NewFile.clicked.connect(self.slotCreateNewFile)

    def initFileUI(self):
        #
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

    @QtCore.pyqtSlot(TableController, PCB, "QString")
    def slotTableRefresh(self, controller, process, operation):
        if operation == "append":
            controller.append(process)
        elif operation == "remove":
            controller.remove(process)
        elif operation == "io_complete":
            controller.edit(process.pid, 11, 'complete')

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


class Shortterm(QThread):
    def __init__(self, ready_pl):
        super().__init__()
        self.ready_pl = ready_pl

    def refreshStatus(self):
        UI_main_window.label_job.setText(str(job_pool.num))
        UI_main_window.label_ready.setText(str(ready_pool.num - 1 if ready_pool.num > 0 else 0))  # except running
        UI_main_window.label_suspended.setText(str(suspend_pool.num))
        UI_main_window.label_terminated.setText(str(terminated_pool.num))
        UI_main_window.label_memory.setText(
            '{:.2f}% ({}/{})'.format(memory.used / TOTAL_MEM * 100, memory.used, TOTAL_MEM))
        UI_main_window.label_references.setText(str(memory.references))
        UI_main_window.label_page_faults.setText(str(memory.page_faults))
        UI_main_window.label_fault_rate.setText(
            '{:.2f}%'.format(0 if memory.references == 0 else memory.page_faults / memory.references * 100))

    def manage_process(self, process, ready_pl):
        process.exec_next_code()
        time.sleep(CPU_PROCESS_TIME)
        ready_pl.after_time_slice(process)

    def run(self):
        while True:
            self.refreshStatus()
            if self.ready_pl.num > 0:
                processing_job = self.ready_pl.get()
                processing_job.status = 'running'
                logger.info('Running {0}...'.format(processing_job.name))
                self.ready_pl.change_priority(processing_job)
                try:
                    self.manage_process(processing_job, self.ready_pl)
                except OutOfMemoryError:
                    pass
            time.sleep(0.001)


class Longterm(QThread):
    def __init__(self, ready_pl, job_pl):
        super().__init__()
        self.ready_pl = ready_pl
        self.job_pl = job_pl

    def run(self):
        while True:
            if self.ready_pl.num < self.ready_pl.count:
                if len(io_pool) > 0:
                    job = io_pool.pop()
                    job.priority = 0
                    suspend_pool.refreshTableSignal.emit(suspend_pool.table_controller, job, "remove")
                else:
                    job = self.job_pl.pop()
                if job:
                    self.ready_pl.add(job)
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


def init_intr_table():
    intr_table.add(0, memory.get_frame)  # 缺页中断
    intr_table.add(1, TimerThread.fromSuspend2Ready)  # io完成中断
    intr_table.add(2, IO.fromReady2Suspend)  # io开始中断
    intr_table.add(3, OutOfMemoryError)  # 异常中断
    intr_table.add(4, time.sleep)  # 时间片中断


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
    io_pool = IOCompletedPool()
    memory = Memory(UI_main_window.rightBarWidget)
    file_chain = Chain()
    UI_main_window.initFileUI()
    intr_table = Intr_table()
    init_intr_table()

    # Show main window
    UI_main_window.show()
    exit(app.exec_())
