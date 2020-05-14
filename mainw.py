# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys
from math import pow

from PyQt5.QtCore import Qt, QObject, pyqtSignal, QUrl, QThread   # QCoreApplication 包含事件主循环 能添加和删除所有事件
from PyQt5.QtGui import QIcon, QFont, QImage, QPixmap, QPalette, QTextCursor
from PyQt5.QtWidgets import (QMainWindow, QApplication, QToolTip, QWidget, QDesktopWidget,
                             QAction, QFileDialog, QMenu, qApp, QGridLayout,
                             QPushButton, QLabel, QCheckBox, QSlider, QLineEdit, QPlainTextEdit,
                             QProgressDialog, QScrollArea, QSizePolicy)

from viewer import ResultViewer

class DebugStream(QObject):
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

class Detection(QThread):
    # signal: return progress + status
    resultProgress = pyqtSignal(int)
    resultStat = pyqtSignal(str)
    resultReady = pyqtSignal()

    def __init__(self, client_obj, fpath):
        super().__init__()
        self.client_obj = client_obj
        self.path = fpath

    def run(self):
        # dialog_upload = QDialog(parent)
        self.resultProgress.emit(50)
        self.resultStat.emit("图像处理中……")
        self.client_obj.detect(self.path)
        self.resultProgress.emit(100)
        self.resultStat.emit("图像处理完毕")
        self.resultReady.emit()

# class ClientGUI(QWidget):
class ClientGUI(QMainWindow):

    def __init__(self):
        # super()构造器方法返回父级对象
        super().__init__()
        QToolTip.setFont(QFont("SansSerif", 10))
        # self.dpi = getDPI()
        # self.setGeometry(150, 150, 1200, 600)     # 坐标 + 大小
        self.resize(900, 450)
        self.setWindowTitle("TF Detection")
        self.setWindowIcon(QIcon("res/icon.png"))
        # self.setToolTip("<b>TF</b> Client")
        self.image_ori = QImage("res/icon.png")

        self.menubar = self.menuBar()               # 初始化菜单栏
        self.widget_main = QWidget(self)
        self.statusbar = self.statusBar()           # 初始化状态栏
        self.initUIMain()                           # 初始化剩余 UI

        sys.stdout = DebugStream(newText=self.debugOut) # 将标准输出改流对象，并设置 signal 发送，利用 slot 更新 PlainTextEdit
        self.setCentralWidget(self.widget_main)     # 主界面

        self.center()
        self.show()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def initUIMain(self):
        # ----- Part1 Actions -----
        act_openfile = QAction("打开文件", self)
        act_openfile.setShortcut("Ctrl+O")
        act_openfile.setStatusTip("打开 JPG 或 PNG 格式图像文件")   # 状态栏提示
        act_openfile.triggered.connect(self.actionOpenFile)

        act_openfolder = QAction("打开文件夹", self)
        act_openfolder.setShortcut("Ctrl+F")
        act_openfolder.setStatusTip("打开文件夹读入图片")   # 状态栏提示
        act_openfolder.triggered.connect(self.actionOpenFolder)

        act_quit = QAction(QIcon("exit.png"), "&退出", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.setStatusTip("退出程序")   # 状态栏提示
        act_quit.triggered.connect(qApp.quit)

        stat_act_statbar = QAction("状态栏", self, checkable=True)
        stat_act_statbar.setStatusTip("是否显示状态栏")
        stat_act_statbar.setChecked(True)
        stat_act_statbar.triggered.connect(self.toggleStatusBar)

        # ----- Part2 控件 -----
        # 图像显示
        self.label_image = QLabel(self.widget_main)
        self.label_image.setMinimumSize(192, 108)
        self.label_image.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.label_image.setAlignment(Qt.AlignCenter)
        # self.label_image.setScaledContents(True)
        self.label_image.setPixmap(QPixmap.fromImage(self.image_ori))
        self.scroll_preview = QScrollArea(self.widget_main)
        self.scroll_preview.setBackgroundRole(QPalette.Dark)
        self.scroll_preview.setWidget(self.label_image)
        # self.hSb = scroll_preview.verticalScrollBar()

        # 服务器地址和端口
        self.label_host = QLabel("主机名")
        # self.lineedit_host = QLineEdit("localhost", self.widget_main)
        self.lineedit_host = QLineEdit("192.168.7.7", self.widget_main)
        self.lineedit_host.setToolTip("服务器的域名或 IP 地址[:端口]")

        # 连接按钮
        self.button_connect = QPushButton("连接", self.widget_main)
        self.button_connect.setToolTip("连接服务器")
        self.button_connect.clicked.connect(self.pressConnect)

        # 打开按钮
        self.lineedit_fpath = QLineEdit("未指定文件", self.widget_main)
        self.lineedit_fpath.setReadOnly(True)
        button_open = QPushButton("打开", self.widget_main)   # QPushButton("text", 父组件)
        button_open.setToolTip("打开 JPG 或 PNG 格式图像文件")
        # instance() 创建一个 QCoreApplication 实例 signal-slot: click -> close
        button_open.clicked.connect(self.actionOpenFile)
        button_open.resize(button_open.sizeHint())  # https://doc.qt.io/qt-5/qwidget.html#sizeHint-prop
        # button_open.move(50, 50)

        # local 开关
        self.chbox_local = QCheckBox("local", self.widget_main)
        self.chbox_local.stateChanged.connect(self.detectMode)
        # verbose 开关
        self.chbox_verbose = QCheckBox("verbose", self.widget_main)

        # 上传按钮
        self.button_upload = QPushButton("上传", self.widget_main)
        self.button_upload.setToolTip("上传图像")
        self.button_upload.clicked.connect(self.startDetect)

        # 预览缩放
        label_silder = QLabel("缩放预览", self.widget_main)
        self.slider_scale = QSlider(Qt.Horizontal)
        # slider_scale.setFocusPolicy(Qt.NoFocus)
        self.slider_scale.setRange(-20, 20)
        self.slider_scale.setValue(0)
        self.slider_scale.valueChanged[int].connect(self.changeScale)
        button_scale_reset = QPushButton("重置", self.widget_main)
        button_scale_reset.setToolTip("重置图像预览的缩放倍数")
        button_scale_reset.clicked.connect(self.pressScaleReset)

        # Debug 信息
        self.textedit_debug = QPlainTextEdit(self.widget_main)
        self.textedit_debug.setReadOnly(True)
        self.textedit_debug.setPlaceholderText("debug info")
        self.textedit_debug.moveCursor(QTextCursor.Start)

        # button_exit = QPushButton("退出", self)
        # button_exit.setToolTip("退出程序")
        # button_exit.clicked.connect(QCoreApplication.instance().quit)

        # ----- Part3 菜单栏 -----
        menu_file = self.menubar.addMenu("&文件")
        menu_open = QMenu("打开", self)
        menu_open.addAction(act_openfile)
        menu_open.addAction(act_openfolder)
        menu_file.addMenu(menu_open)
        menu_file.addAction(act_quit)

        menu_window = self.menubar.addMenu("&窗口")
        menu_window.addAction(stat_act_statbar)

        # menu_help = self.menubar.addMenu("&帮助")

        # ----- Part4 工具栏 -----

        # ------ Part5 主界面 -----
        layout_main = QGridLayout(self.widget_main)
        layout_main.setSpacing(8) # sets both the vertical and horizontal spacing to spacing

        layout_main.addWidget(self.scroll_preview,  1, 1, 5, 1)

        layout_main.addWidget(self.label_host,      1, 2)
        layout_main.addWidget(self.lineedit_host,   1, 3, 1, 2)
        layout_main.addWidget(self.button_connect,  1, 5)

        layout_main.addWidget(self.lineedit_fpath,  2, 2, 1, 3)
        layout_main.addWidget(button_open,          2, 5)

        layout_main.addWidget(self.chbox_local,     3, 2)
        layout_main.addWidget(self.chbox_verbose,   3, 3)
        layout_main.addWidget(self.button_upload,        3, 5)

        layout_main.addWidget(label_silder,         4, 2)
        layout_main.addWidget(self.slider_scale,    4, 3, 1, 2)
        layout_main.addWidget(button_scale_reset,   4, 5)

        layout_main.addWidget(self.textedit_debug,  5, 2, 1, 4)
        # self.widget_main.setLayout(layout_main)

        # ----- Part6 状态栏 -----
        self.statusbar.showMessage("就绪")

    def actionOpenFile(self):
        self.file_path = QFileDialog.getOpenFileUrl(self, "打开文件", filter="Images (*.png *.jpg)")
        if not self.file_path[0].isValid():
            return
        self.file_name = self.file_path[0].fileName()
        self.file_path = self.file_path[0].toLocalFile()
        self.lineedit_fpath.setText(self.file_path)
        self.image_ori = QImage(self.file_path)
        self.slider_scale.setValue(0)
        # self.newText.emit(str(text))
        self.slider_scale.valueChanged.emit(0)  # 必须强制发送一次，否则如果上次未变化，会没有这个消息
        # self.label_image.setGeometry(0, 0, self.image_ori.width(), self.image_ori.height())
        # self.label_image.setPixmap(QPixmap.fromImage(self.image_ori))
        print("打开 " + self.file_path)

    def actionOpenFolder(self):
        self.folder_path = QFileDialog.getExistingDirectoryUrl(self, "打开文件夹")
        if not self.folder_path.isValid():
            return
        self.folder_name = self.folder_path.fileName()
        self.folder_path = self.folder_path.toLocalFile()
        self.lineedit_fpath.setText(self.folder_path)
        print("打开 " + self.folder_path)

    def toggleStatusBar(self, state):
        if state:
            self.statusbar.show()
        else:
            self.statusbar.hide()

    def pressConnect(self):
        if not self.chbox_local.isChecked():
            from mrcnn.model_client import MaskRCNNClient
            url = QUrl("https://" + self.lineedit_host.text(), QUrl.StrictMode)
            host = url.host() + ":" + str(url.port(8500))
            self.client_obj = MaskRCNNClient(host)
            if self.client_obj:
                print('connected to', host)

    def detectMode(self, state):
        if state:
            self.label_host.hide()
            self.lineedit_host.hide()
            self.button_connect.hide()
            self.button_upload.setText("检测")
        else:
            self.label_host.show()
            self.lineedit_host.show()
            self.button_connect.show()
            self.button_upload.setText("上传")

    def startDetect(self):
        progressdialog_detect = QProgressDialog("准备执行检测……", "取消", 0, 100, self.widget_main)
        if self.chbox_local.isChecked():
            print("preparing model...")
            from mrcnn.model_local import MaskRCNNLocal
            self.client_obj = MaskRCNNLocal()
        # if self.lineedit_fpath == self.file_path:
        self.thread_detect = Detection(self.client_obj, self.file_path)
        self.thread_detect.resultProgress.connect(progressdialog_detect.setValue)
        self.thread_detect.resultStat.connect(progressdialog_detect.setLabelText)
        # Detection.resultReady.connect(self.preview)  # Detection 线程类的 resultReady signal 插入 preview slot
        self.thread_detect.resultReady.connect(self.preview)  # Detection 线程对象的 resultReady signal 插入 preview slot
        progressdialog_detect.canceled.connect(self.thread_detect.exit)
        self.thread_detect.start()
        # elif self.lineedit_fpath == self.folder_path:
        # TODO 检测文件变化

    def pressScaleReset(self):
        self.slider_scale.setValue(0)

    def changeScale(self, value):
        if value:
            scale = pow(10.0, value/20.0)
            scaled_img = self.image_ori.scaled(self.image_ori.width()*scale, self.image_ori.height()*scale, Qt.KeepAspectRatio)
        else:
            scaled_img = self.image_ori
        self.label_image.setGeometry(0, 0, scaled_img.width(), scaled_img.height())
        self.label_image.setPixmap(QPixmap.fromImage(scaled_img))

    # slot: preview
    def preview(self):
        detect_result = self.thread_detect.client_obj
        if self.chbox_verbose.isChecked():
            detect_result.debug()
        print("visualizing...")
        self.mainwin_viewer = ResultViewer(detect_result, self)

    # slot: debugOut
    def debugOut(self, text):
        # self.textedit_debug.appendPlainText(text)
        cursor = self.textedit_debug.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.textedit_debug.setTextCursor(cursor)

    def center(self):
        qr = self.frameGeometry()  # 获得主窗口所在框架
        # QtGui.QDesktopWidget 提供用户桌面信息 包括屏幕大小
        cp = QDesktopWidget().availableGeometry().center()  # 获取显示器分辨率后得到屏幕中间点位置
        qr.moveCenter(cp)  # 将主窗口框架中心点放置于屏幕中心
        self.move(qr.topLeft())  # 通过 move 函数将主窗口左上角移动至其框架左上角
