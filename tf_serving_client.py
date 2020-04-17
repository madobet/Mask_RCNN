#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
import sys
import argparse
from mrcnn.model_client import MaskRCNNClient
from PyQt5.QtWidgets import QApplication, qApp, QStyleFactory
from PyQt5.QtCore import QUrl
from mainw import ClientGUI

# plot format
from matplotlib import rcParams
rcParams['font.family'] = ['sans-serif']
rcParams['font.weight'] = 'semibold'
rcParams['font.size'] = 14
rcParams['font.sans-serif'] = ['Sarasa Gothic SC', 'SimHei', 'sans-serif']
# rcParams['axes.unicode_minus'] = False
# from matplotlib.font_manager import _rebuild
# _rebuild()

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

IS_DEBUG = False

def clientCLI(host, fpath, opath=None):
    grpc_ser = MaskRCNNClient(host)
    grpc_ser.grpc_request(fpath)
    if IS_DEBUG:
        grpc_ser.debug()
    print('Visualizing result...')
    pix_width = QApplication.desktop().width()
    pix_height = QApplication.desktop().height()
    dpi_x = qApp.desktop().logicalDpiX()
    dpi_y = qApp.desktop().logicalDpiY()
    print("Screen: %d, %d\nDPI: %d, %d" % (pix_width, pix_height, dpi_x, dpi_y))
    grpc_ser.display("Mask RCNN Demo", (pix_width/dpi_x, pix_height/dpi_y), fpath=opath)

from PyQt5.QtQuick import QQuickView

def clientGUI():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    w = ClientGUI()
    sys.exit(app.exec_())

def entry():
    preparser = argparse.ArgumentParser(add_help=False)
    preparser.add_argument('--nogui', action='store_true')
    args_parsered, args_rest = preparser.parse_known_intermixed_args()  # GUI 确认后交给下一解析器
    if not args_parsered.nogui:
        clientGUI()
        return

    parser = argparse.ArgumentParser(
        description='Client for Tensorflow Serving of Mask RCNN',
        epilog='使用例：./tf_serving_client.py 127.0.0.1 ./just4fun/foo.png -o ~/bar.jpg')
    parser.add_argument('--nogui', action='store_true',
                        help='使用命令行（默认启动图形界面）')
    parser.add_argument('host', metavar='(DOMAIN|IP)', help='服务器域名或 IP')
    parser.add_argument('file', metavar='FILE', help='待处理的图像文件路径')
    parser.add_argument('-p', '--port', metavar='PORT',
                        default='8500', help='通信端口（默认：8500）')
    parser.add_argument('-o', '--out', metavar='OUTPUT',
                        default=None, help='处理后的图像文件输出路径（不指定则输出到屏幕）')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='打印调试信息')
    args = parser.parse_intermixed_args()
    global IS_DEBUG; IS_DEBUG = args.verbose
    clientCLI(args.host + ':' + args.port,
              os.path.abspath(args.file), os.path.abspath(args.out))

if __name__ == '__main__':
    entry()
