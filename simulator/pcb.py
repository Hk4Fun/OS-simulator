import random

from .code import instructions
from .errors import *
from .memory import memory

used_PIDs = set()


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
        from .pool import terminated_pool, ready_pool
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
