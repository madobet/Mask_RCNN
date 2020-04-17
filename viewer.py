# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import matplotlib
# Make sure that we are using QT5
matplotlib.use("Qt5Agg")
# sets up a Matplotlib canvas FigureCanvasQTAgg which creates the Figure and adds a single set of axes to it.
# This canvas object is also a QWidget and so can be embedded straight into an application as any other Qt widget.
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NaviTool
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, qApp, QDesktopWidget, QSizePolicy, QMainWindow, QToolBar, QAction, QStyle, QMessageBox

class MplCanvas(FigureCanvas):
    """
    Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.).
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        # self.axes = fig.add_subplot()
        self.axes = fig.add_axes([0.0, 0.0, 1.0, 1.0])

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class ResultViewer(QMainWindow):

    def __init__(self, result, parent=None, width=1366, height=768, dpi=100):
        """
        :param result: MaskRCNNClient 类
        """
        super().__init__(parent)
        self.menubar = self.menuBar()             # 初始化菜单栏
        self.detect_result = result
        pix_width = QApplication.desktop().width()
        pix_height = QApplication.desktop().height()
        dpi_x = qApp.desktop().logicalDpiX()
        dpi_y = qApp.desktop().logicalDpiY()
        print("Screen: %d, %d\nDPI: %d, %d" % (pix_width, pix_height, dpi_x, dpi_y))
        self.mpl_preview = MplCanvas(self, pix_width/dpi_x, pix_height/dpi_y, (dpi_x + dpi_y)/2)
        # self.mpl_preview = MplCanvas(self)
        self.initUIMain()                         # 初始化剩余 UI

        self.resize(1200, 675)
        self.setWindowTitle("TF Viewer")
        self.setWindowIcon(QIcon("res/icon.png"))

        self.setCentralWidget(self.mpl_preview)   # 主界面
        self.visual_result()

        self.center()
        self.show()

    def initUIMain(self):
        # ----- Part1 Actions -----
        act_savefile = QAction("保存", self)
        act_savefile.setShortcut("Ctrl+S")
        act_savefile.triggered.connect(self.actionSaveFile)

        act_close = QAction("关闭", self)
        act_close.triggered.connect(self.close)

        self.stat_act_mask = QAction("掩膜", self, checkable=True)
        self.stat_act_mask.setStatusTip("在图像上叠加显示掩膜")
        self.stat_act_mask.setChecked(True)
        self.stat_act_mask.toggled.connect(self.toggleViewMaskBoxLabel)

        self.stat_act_bbox = QAction("边界框", self, checkable=True)
        self.stat_act_bbox.setStatusTip("在图像上叠加显示边界框")
        self.stat_act_bbox.setChecked(True)
        self.stat_act_bbox.toggled.connect(self.toggleViewMaskBoxLabel)

        self.stat_act_label = QAction("标签", self, checkable=True)
        self.stat_act_label.setStatusTip("在图像上叠加显示标签")
        self.stat_act_label.setChecked(True)
        self.stat_act_label.toggled.connect(self.toggleViewMaskBoxLabel)

        # ----- Part2 控件 -----

        # ----- Part3 菜单栏 -----
        menu_file = self.menubar.addMenu("&文件")
        menu_file.addAction(act_savefile)
        menu_file.addAction(act_close)

        menu_view = self.menubar.addMenu("&视图")
        menu_view.addAction(self.stat_act_mask)
        menu_view.addAction(self.stat_act_bbox)
        menu_view.addAction(self.stat_act_label)

        # ----- Part4 工具栏 -----
        navitoolbar = NaviTool(self.mpl_preview, self)
        self.addToolBar(Qt.TopToolBarArea, navitoolbar)

        toolbar = QToolBar(floatable=False, floating=False, movable=False)
        self.addToolBar(Qt.BottomToolBarArea, toolbar)  # 初始化工具栏
        toolbar.addAction(self.stat_act_mask)
        toolbar.addAction(self.stat_act_bbox)
        toolbar.addAction(self.stat_act_label)

    def actionSaveFile(self):
        return

    def toggleViewMaskBoxLabel(self, state):
        self.detect_result.display(axes=self.mpl_preview.axes,
                                   show_mask=self.stat_act_mask.isChecked(),
                                   show_bbox=self.stat_act_bbox.isChecked(),
                                   show_label=self.stat_act_label.isChecked())
        self.mpl_preview.draw()

    def visual_result(self):
        self.detect_result.display(axes=self.mpl_preview.axes)
        self.mpl_preview.draw()

    def closeEvent(self, event):
        """
        由关闭 QWidget 产生的 QCloseEvent 所引发的 closeEvent 回调
        :param event: 事件
        :return: event.accept() 或 event.ignore()
        """
        reply = QMessageBox.question(self, "TF Client",
            "要在退出前存储处理后的图像吗？", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

    def center(self):
        qr = self.frameGeometry()  # 获得主窗口所在框架
        # QtGui.QDesktopWidget 提供用户桌面信息 包括屏幕大小
        cp = QDesktopWidget().availableGeometry().center()  # 获取显示器分辨率后得到屏幕中间点位置
        qr.moveCenter(cp)  # 将主窗口框架中心点放置于屏幕中心
        self.move(qr.topLeft())  # 通过 move 函数将主窗口左上角移动至其框架左上角
