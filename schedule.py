import time

from PyQt5.QtCore import QThread

from settings import *
from errors import *
from memory import memory
from pool import ready_pool, terminated_pool, job_pool, suspend_pool, io_pool
from mainwindow import UI_main_window


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
