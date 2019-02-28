# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'file_edit.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(511, 383)
        font = QtGui.QFont()
        font.setPointSize(14)
        Dialog.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.AddJobNameLabel_2 = QtWidgets.QLabel(Dialog)
        self.AddJobNameLabel_2.setObjectName("AddJobNameLabel_2")
        self.horizontalLayout.addWidget(self.AddJobNameLabel_2)
        self.AddJobPriorityEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.AddJobPriorityEdit_2.setObjectName("AddJobPriorityEdit_2")
        self.horizontalLayout.addWidget(self.AddJobPriorityEdit_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.AddJobPriorityLabel_2 = QtWidgets.QLabel(Dialog)
        self.AddJobPriorityLabel_2.setObjectName("AddJobPriorityLabel_2")
        self.horizontalLayout_2.addWidget(self.AddJobPriorityLabel_2)
        self.AddJobNameEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.AddJobNameEdit_2.setObjectName("AddJobNameEdit_2")
        self.horizontalLayout_2.addWidget(self.AddJobNameEdit_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.JobText = QtWidgets.QTextEdit(Dialog)
        self.JobText.setObjectName("JobText")
        self.verticalLayout.addWidget(self.JobText)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.saveFileButton = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(14)
        self.saveFileButton.setFont(font)
        self.saveFileButton.setAutoDefault(False)
        self.saveFileButton.setObjectName("saveFileButton")
        self.horizontalLayout_10.addWidget(self.saveFileButton)
        self.addJobButton = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.addJobButton.setFont(font)
        self.addJobButton.setCheckable(True)
        self.addJobButton.setChecked(True)
        self.addJobButton.setObjectName("addJobButton")
        self.horizontalLayout_10.addWidget(self.addJobButton)
        self.deleteFileButton = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(14)
        self.deleteFileButton.setFont(font)
        self.deleteFileButton.setObjectName("deleteFileButton")
        self.horizontalLayout_10.addWidget(self.deleteFileButton)
        self.verticalLayout.addLayout(self.horizontalLayout_10)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.AddJobNameLabel_2.setText(_translate("Dialog", "作业名称"))
        self.AddJobPriorityLabel_2.setText(_translate("Dialog", "优先权值"))
        self.JobText.setPlaceholderText(_translate("Dialog", "Your Codes"))
        self.saveFileButton.setText(_translate("Dialog", "保存"))
        self.addJobButton.setText(_translate("Dialog", "添加任务"))
        self.deleteFileButton.setText(_translate("Dialog", "删除"))

