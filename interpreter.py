__author__ = 'Hk4Fun'
__date__ = '2018/9/21 1:07'


class Intr_table:
    def __init__(self):
        self.intr_dict = {}

    def query(self, intr_num):
        return self.intr_dict[intr_num]

    def add(self, intr_num, func_addr):
        self.intr_dict[intr_num] = func_addr


class PCBTable:
    def __init__(self):
        self.stack = []

    def pushPCB(PCB, self):
        self.stack.append(PCB)

    def popPCB(PCB, self):
        return self.stack.pop()
