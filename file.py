from PyQt5.QtWidgets import QMessageBox, QDialog

from ui import file
from pool import job_pool
from errors import CodeFormatError
from pcb import PCB


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


class FileEditDialog(QDialog, file.Ui_Dialog):
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


file_chain = Chain()
