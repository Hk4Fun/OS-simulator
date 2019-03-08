import threading
import logging
import time
from collections import namedtuple

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidgetItem

from .settings import *
from .utils import mutex_lock
from .errors import OutOfMemoryError
from .mainwindow import ui_mainwindow

logger = logging.getLogger('log')


class PTE:
    __slots__ = ['frame', 'recent_access_time', 'valid_bit']

    def __init__(self, frame, recent_access_time, valid_bit):
        self.frame = frame
        self.recent_access_time = recent_access_time
        self.valid_bit = valid_bit


class Memory(QtCore.QObject):
    memory_edit_signal = QtCore.pyqtSignal("QString", int)

    def __init__(self, table):
        super().__init__()
        self.table = table
        self.lock = threading.Lock()
        self.free_frames = list(range(TOTAL_MEM))
        self.memory_edit_signal.connect(ui_mainwindow.slotMemoryTableEdit)
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
                "{} requests page {}. This page is already in memory frame {}".format(process.pid, page_num, frame))
        else:
            # PAGE FAULT!!!!
            self.page_faults += 1
            process.page_faults += 1
            free_frame = self.get_frame()
            self._edit_table_widget("allocate", free_frame)
            process.page_table[page_num] = PTE(free_frame, time.time(), True)
            logger.info(
                "{} requests page {}. Page Fault occurred. Frame {} granted".format(process.pid, page_num, free_frame))

    def get_frame(self):
        if len(self.free_frames) != 0:
            return self.free_frames.pop(0)
        else:
            # we have to boot lru add frame to free list, and return it
            self.replace_by_lru()
            return self.free_frames.pop(0)

    def replace_by_lru(self):
        from .pool import ready_pool
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


memory = Memory(ui_mainwindow.rightBarWidget)
