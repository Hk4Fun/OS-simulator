# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(1197, 620)
        font = QtGui.QFont()
        font.setPointSize(9)
        MainWindow.setFont(font)
        MainWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.centralwidget.setFont(font)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.BottomLayout = QtWidgets.QHBoxLayout()
        self.BottomLayout.setObjectName("BottomLayout")
        self.DaoshuLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DaoshuLabel.setFont(font)
        self.DaoshuLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.DaoshuLabel.setObjectName("DaoshuLabel")
        self.BottomLayout.addWidget(self.DaoshuLabel)
        self.DaoshuBox = QtWidgets.QSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DaoshuBox.setFont(font)
        self.DaoshuBox.setMinimum(1)
        self.DaoshuBox.setMaximum(10)
        self.DaoshuBox.setObjectName("DaoshuBox")
        self.BottomLayout.addWidget(self.DaoshuBox)
        self.StartButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.StartButton.setFont(font)
        self.StartButton.setAutoDefault(False)
        self.StartButton.setDefault(True)
        self.StartButton.setObjectName("StartButton")
        self.BottomLayout.addWidget(self.StartButton)
        self.horizontalLayout_5.addLayout(self.BottomLayout)
        self.NowRunningLabel = QtWidgets.QLabel(self.centralwidget)
        self.NowRunningLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.NowRunningLabel.setObjectName("NowRunningLabel")
        self.horizontalLayout_5.addWidget(self.NowRunningLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.RandomCountBox = QtWidgets.QSpinBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.RandomCountBox.setFont(font)
        self.RandomCountBox.setMinimum(1)
        self.RandomCountBox.setMaximum(1000)
        self.RandomCountBox.setObjectName("RandomCountBox")
        self.horizontalLayout.addWidget(self.RandomCountBox)
        self.GenerateJobButton = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.GenerateJobButton.setFont(font)
        self.GenerateJobButton.setObjectName("GenerateJobButton")
        self.horizontalLayout.addWidget(self.GenerateJobButton)
        self.horizontalLayout_5.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.groupBox = QtWidgets.QGroupBox(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.JobPoolTable = QtWidgets.QTableWidget(self.groupBox)
        self.JobPoolTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.JobPoolTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.JobPoolTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.JobPoolTable.setObjectName("JobPoolTable")
        self.JobPoolTable.setColumnCount(5)
        self.JobPoolTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.JobPoolTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.JobPoolTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.JobPoolTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.JobPoolTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.JobPoolTable.setHorizontalHeaderItem(4, item)
        self.JobPoolTable.horizontalHeader().setVisible(True)
        self.JobPoolTable.horizontalHeader().setHighlightSections(True)
        self.JobPoolTable.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.JobPoolTable)
        self.groupBox_2 = QtWidgets.QGroupBox(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.ReadyTable = QtWidgets.QTableWidget(self.groupBox_2)
        self.ReadyTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.ReadyTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ReadyTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ReadyTable.setObjectName("ReadyTable")
        self.ReadyTable.setColumnCount(7)
        self.ReadyTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.ReadyTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.ReadyTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.ReadyTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.ReadyTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.ReadyTable.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.ReadyTable.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.ReadyTable.setHorizontalHeaderItem(6, item)
        self.ReadyTable.verticalHeader().setVisible(False)
        self.verticalLayout_2.addWidget(self.ReadyTable)
        self.groupBox_3 = QtWidgets.QGroupBox(self.splitter)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.SuspendTable = QtWidgets.QTableWidget(self.groupBox_3)
        self.SuspendTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.SuspendTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.SuspendTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.SuspendTable.setObjectName("SuspendTable")
        self.SuspendTable.setColumnCount(7)
        self.SuspendTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.SuspendTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.SuspendTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.SuspendTable.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.SuspendTable.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.SuspendTable.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.SuspendTable.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.SuspendTable.setHorizontalHeaderItem(6, item)
        self.SuspendTable.verticalHeader().setVisible(False)
        self.verticalLayout_3.addWidget(self.SuspendTable)
        self.verticalLayout_4.addWidget(self.splitter)
        self.horizontalLayout_6.addLayout(self.verticalLayout_4)
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setOpaqueResize(True)
        self.splitter_2.setHandleWidth(5)
        self.splitter_2.setChildrenCollapsible(True)
        self.splitter_2.setObjectName("splitter_2")
        self.AddJobTabWidget = QtWidgets.QTabWidget(self.splitter_2)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.AddJobTabWidget.setFont(font)
        self.AddJobTabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.AddJobTabWidget.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.AddJobTabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.AddJobTabWidget.setDocumentMode(True)
        self.AddJobTabWidget.setTabsClosable(False)
        self.AddJobTabWidget.setMovable(True)
        self.AddJobTabWidget.setTabBarAutoHide(False)
        self.AddJobTabWidget.setObjectName("AddJobTabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.formLayout = QtWidgets.QFormLayout(self.tab)
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_5 = QtWidgets.QLabel(self.tab)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_job = QtWidgets.QLabel(self.tab)
        self.label_job.setObjectName("label_job")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.label_job)
        self.label_ready = QtWidgets.QLabel(self.tab)
        self.label_ready.setObjectName("label_ready")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_ready)
        self.label_suspended = QtWidgets.QLabel(self.tab)
        self.label_suspended.setObjectName("label_suspended")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.label_suspended)
        self.label_terminated = QtWidgets.QLabel(self.tab)
        self.label_terminated.setObjectName("label_terminated")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.label_terminated)
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setObjectName("label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_memory = QtWidgets.QLabel(self.tab)
        self.label_memory.setObjectName("label_memory")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.label_memory)
        self.AddJobTabWidget.addTab(self.tab, "")
        self.AddJobTabWidgetPage1 = QtWidgets.QWidget()
        self.AddJobTabWidgetPage1.setObjectName("AddJobTabWidgetPage1")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.AddJobTabWidgetPage1)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.AddJobNameLabel = QtWidgets.QLabel(self.AddJobTabWidgetPage1)
        self.AddJobNameLabel.setObjectName("AddJobNameLabel")
        self.horizontalLayout_2.addWidget(self.AddJobNameLabel)
        self.AddJobNameEdit = QtWidgets.QLineEdit(self.AddJobTabWidgetPage1)
        self.AddJobNameEdit.setObjectName("AddJobNameEdit")
        self.horizontalLayout_2.addWidget(self.AddJobNameEdit)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.AddJobPriorityLabel = QtWidgets.QLabel(self.AddJobTabWidgetPage1)
        self.AddJobPriorityLabel.setObjectName("AddJobPriorityLabel")
        self.horizontalLayout_3.addWidget(self.AddJobPriorityLabel)
        self.AddJobPriorityEdit = QtWidgets.QLineEdit(self.AddJobTabWidgetPage1)
        self.AddJobPriorityEdit.setObjectName("AddJobPriorityEdit")
        self.horizontalLayout_3.addWidget(self.AddJobPriorityEdit)
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.AddJobTimeLabel = QtWidgets.QLabel(self.AddJobTabWidgetPage1)
        self.AddJobTimeLabel.setObjectName("AddJobTimeLabel")
        self.horizontalLayout_4.addWidget(self.AddJobTimeLabel)
        self.AddJobMemoryEdit = QtWidgets.QLineEdit(self.AddJobTabWidgetPage1)
        self.AddJobMemoryEdit.setObjectName("AddJobMemoryEdit")
        self.horizontalLayout_4.addWidget(self.AddJobMemoryEdit)
        self.verticalLayout_6.addLayout(self.horizontalLayout_4)
        self.JobText = QtWidgets.QTextEdit(self.AddJobTabWidgetPage1)
        self.JobText.setObjectName("JobText")
        self.verticalLayout_6.addWidget(self.JobText)
        self.AddJobButton = QtWidgets.QPushButton(self.AddJobTabWidgetPage1)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.AddJobButton.setFont(font)
        self.AddJobButton.setObjectName("AddJobButton")
        self.verticalLayout_6.addWidget(self.AddJobButton)
        self.verticalLayout_6.setStretch(0, 1)
        self.verticalLayout_6.setStretch(1, 1)
        self.verticalLayout_6.setStretch(2, 1)
        self.verticalLayout_6.setStretch(3, 4)
        self.verticalLayout_6.setStretch(4, 2)
        self.AddJobTabWidget.addTab(self.AddJobTabWidgetPage1, "")
        self.FinishedGroupBox = QtWidgets.QGroupBox(self.splitter_2)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.FinishedGroupBox.setFont(font)
        self.FinishedGroupBox.setObjectName("FinishedGroupBox")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.FinishedGroupBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.TerminatedTable = QtWidgets.QTableWidget(self.FinishedGroupBox)
        self.TerminatedTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.TerminatedTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.TerminatedTable.setObjectName("TerminatedTable")
        self.TerminatedTable.setColumnCount(2)
        self.TerminatedTable.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.TerminatedTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TerminatedTable.setHorizontalHeaderItem(1, item)
        self.TerminatedTable.verticalHeader().setVisible(False)
        self.verticalLayout_5.addWidget(self.TerminatedTable)
        self.horizontalLayout_6.addWidget(self.splitter_2)
        self.rightBarWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.rightBarWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.rightBarWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.rightBarWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.rightBarWidget.setAlternatingRowColors(False)
        self.rightBarWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.rightBarWidget.setShowGrid(False)
        self.rightBarWidget.setObjectName("rightBarWidget")
        self.rightBarWidget.setColumnCount(1)
        self.rightBarWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.rightBarWidget.setHorizontalHeaderItem(0, item)
        self.rightBarWidget.horizontalHeader().setVisible(False)
        self.rightBarWidget.verticalHeader().setVisible(False)
        self.horizontalLayout_6.addWidget(self.rightBarWidget)
        self.horizontalLayout_6.setStretch(0, 22)
        self.horizontalLayout_6.setStretch(1, 6)
        self.horizontalLayout_6.setStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1197, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.AddJobTabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "调度模拟"))
        self.DaoshuLabel.setText(_translate("MainWindow", "Ready 道数"))
        self.StartButton.setText(_translate("MainWindow", "开始运行"))
        self.NowRunningLabel.setText(_translate("MainWindow", "Running:"))
        self.GenerateJobButton.setText(_translate("MainWindow", "随机生成任务"))
        self.groupBox.setTitle(_translate("MainWindow", "Job"))
        item = self.JobPoolTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "PID"))
        item = self.JobPoolTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "作业名称"))
        item = self.JobPoolTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "状态"))
        item = self.JobPoolTable.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "优先权"))
        item = self.JobPoolTable.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "所需内存"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Ready"))
        item = self.ReadyTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "PID"))
        item = self.ReadyTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "作业名称"))
        item = self.ReadyTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "状态"))
        item = self.ReadyTable.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "优先权"))
        item = self.ReadyTable.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "所需内存"))
        item = self.ReadyTable.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "PCB指针"))
        item = self.ReadyTable.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "PC"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Suspended"))
        item = self.SuspendTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "PID"))
        item = self.SuspendTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "作业名称"))
        item = self.SuspendTable.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "状态"))
        item = self.SuspendTable.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "优先权"))
        item = self.SuspendTable.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "所需内存"))
        item = self.SuspendTable.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "PCB指针"))
        item = self.SuspendTable.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "PC"))
        self.label_3.setText(_translate("MainWindow", "Job："))
        self.label_5.setText(_translate("MainWindow", "Ready："))
        self.label_2.setText(_translate("MainWindow", "Suspended："))
        self.label_4.setText(_translate("MainWindow", "Terminated："))
        self.label_job.setText(_translate("MainWindow", "0"))
        self.label_ready.setText(_translate("MainWindow", "0"))
        self.label_suspended.setText(_translate("MainWindow", "0"))
        self.label_terminated.setText(_translate("MainWindow", "0"))
        self.label.setText(_translate("MainWindow", "Memory："))
        self.label_memory.setText(_translate("MainWindow", "0"))
        self.AddJobTabWidget.setTabText(self.AddJobTabWidget.indexOf(self.tab), _translate("MainWindow", "当前状态"))
        self.AddJobNameLabel.setText(_translate("MainWindow", "作业名称"))
        self.AddJobPriorityLabel.setText(_translate("MainWindow", "优先权值"))
        self.AddJobTimeLabel.setText(_translate("MainWindow", "占用内存"))
        self.JobText.setPlaceholderText(_translate("MainWindow", "Your Codes"))
        self.AddJobButton.setText(_translate("MainWindow", "添加"))
        self.AddJobTabWidget.setTabText(self.AddJobTabWidget.indexOf(self.AddJobTabWidgetPage1), _translate("MainWindow", "添加任务"))
        self.FinishedGroupBox.setTitle(_translate("MainWindow", "Terminated"))
        item = self.TerminatedTable.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "PID"))
        item = self.TerminatedTable.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "作业名称"))
        item = self.rightBarWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "column1"))

