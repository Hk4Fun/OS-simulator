import logging
from abc import ABCMeta, abstractmethod

from PyQt5.QtCore import QThread, QTimer

from .settings import CPU_PROCESS_TIME
from .memory import memory

logger = logging.getLogger('log')


class TimerThread(QThread):
    def __init__(self, process, exectime):
        super().__init__()
        self.process = process
        self.exectime = exectime

    def fromSuspend2Ready(self):
        logger.info("Resume {}".format(self.process.name))
        self.process.io_status = 'complete'
        from .pool import suspend_pool
        suspend_pool.remove(self.process)
        self.process.pc += 1

    def run(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.fromSuspend2Ready)
        self.timer.start(self.exectime * 1000)
        self.exec_()


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
        from .pool import ready_pool, terminated_pool
        logger.info('{0} terminated'.format(self.process.name))
        ready_pool.remove(self.process.pid)  # remove job from waiting list
        memory.free(self.process)  # free memory
        terminated_pool.add(self.process)  # add to terminated pool
        if len(ready_pool._pool) == 0:
            ready_pool.running_label_change_signal.emit("")


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
        from .pool import ready_pool, suspend_pool
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
    def __init__(self, filename, exectime, process):
        super().__init__(exectime, process)
        self.filename = filename

    def change_io_type(self):
        self.process.io_type = 'write file'


instructions = {'C': C,
                'K': K,
                'P': P,
                'R': R,
                'W': W,
                'Q': Q}
