#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sys
import argparse
from PyQt5.QtWidgets import QApplication, QWidget
# 引入了PyQt5.QtWidgets模块，这个模块包含了基本的组件。
from mrcnn.model_client import MaskRCNNClient

def get_dpi():
    app = QApplication(sys.argv)
    screen = app.screens()[0]
    dpi = screen.physicalDotsPerInch()
    app.quit()
    return dpi

def client_cli(host, fpath, opath=None):
    grpc_ser = MaskRCNNClient(host)
    grpc_ser.grpc_request(fpath)
    # grpc_ser.debug()
    if opath:
        dpi = get_dpi()
        grpc_ser.display((1432/dpi, 1080/dpi), opath)
    else:
        grpc_ser.display()

def client_gui():
    app = QApplication(sys.argv)
    # 每个PyQt5应用都必须创建一个应用对象。sys.argv是一组命令行参数的列表。
    # Python可以在shell里运行，这个参数提供对脚本控制的功能。
    w = QWidget()
    # QWidge 控件是用户界面基本控件，提供了基本的应用构造器。
    # 默认情况下，构造器是没有父级的，没有父级的构造器被称为窗口（window）。
    w.resize(800, 600)  # resize() 方法改变控件的大小
    w.move(300, 600)
    # move()是修改控件位置的的方法。它把控件放置到屏幕坐标的(300, 300)的位置。注：屏幕坐标系的原点是屏幕的左上角。
    w.setWindowTitle('Tensorflow Serving Client')
    # 我们给这个窗口添加了一个标题，标题在标题栏展示（虽然这看起来是一句废话，但是后面还有各种栏，还是要注意一下，多了就蒙了）。
    w.show()
    # show()能让控件在桌面上显示出来。控件在内存里创建，之后才能在显示器上显示出来。
    sys.exit(app.exec_())
    # 进入了应用的主循环中，事件处理器这个时候开始工作。主循环从窗口上接收事件，并把事件传入到派发到应用控件里。
    # 当调用exit()方法或直接销毁主控件时，主循环就会结束。sys.exit()方法能确保主循环安全退出。外部环境能通知主控件怎么结束。
    # exec_()之所以有个下划线，是因为exec是一个Python的关键字。

class ClientGUI(QWidget):
    def __init__(self):
        # super()构造器方法返回父级对象。__init__()方法是构造器的一个方法。
        super().__init__()
        self.initUI()

def entry():
    # 先进行 GUI 的确认，然后交给下一个解析器
    preparser = argparse.ArgumentParser(add_help=False)
    preparser.add_argument('--gui', action='store_true')
    args_parsered, args_rest = preparser.parse_known_intermixed_args()
    if args_parsered.gui:
        client_gui()
        return

    parser = argparse.ArgumentParser(
        description='Client for Tensorflow Serving of Mask RCNN',
        epilog='使用例：./tf_serving_client.py 127.0.0.1 ./just4fun/foo.png -o ~/bar.jpg')
    parser.add_argument('--gui', action='store_true',
                        help='使用图形界面（所有命令行选项都将失效）')
    parser.add_argument('host', metavar='(DOMAIN|IP)', help='服务器域名或 IP')
    parser.add_argument('file', metavar='FILE', help='待处理的图像文件路径')
    parser.add_argument('-p', '--port', metavar='PORT',
                        default='8500', help='通信端口（默认：8500）')
    parser.add_argument('-o', '--out', metavar='OUTPUT',
                        default=None, help='处理后的图像文件输出路径（不指定则输出到屏幕）')
    args = parser.parse_intermixed_args()
    client_cli(args.host + ':' + args.port,
               os.path.abspath(args.file), os.path.abspath(args.out))


if __name__ == '__main__':
    entry()
