#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os, sys, argparse

# plot format
from matplotlib import rcParams
rcParams['font.family'] = ['sans-serif']
rcParams['font.weight'] = 'semibold'
rcParams['font.size'] = 20
rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'SimHei', 'sans-serif']
# rcParams['axes.unicode_minus'] = False
# from matplotlib.font_manager import _rebuild
# _rebuild()

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

IS_DEBUG = False

def clientCLI(fpath, host=None, opath=None, width=1920, height=1080, dpi=96):
    if host:
        from mrcnn.model_client import MaskRCNNClient
        grpc_ser = MaskRCNNClient(host)
        grpc_ser.grpc_request(fpath)
        if IS_DEBUG:
            grpc_ser.debug()
        if os.path.splitext(opath)[-1] == ".json":
            grpc_ser.out2json(opath=opath)
        else:
            print('Visualizing result...')
            dpi_x: int = dpi
            dpi_y: int = dpi
            print("Size: %d, %d\nDPI: %d, %d" % (width, height, dpi_x, dpi_y))
            grpc_ser.display(None, (width/dpi_x, height/dpi_y), fpath=opath)
    else:
        from mrcnn.model_local import MaskRCNNLocal
        local_detect = MaskRCNNLocal()
        if IS_DEBUG:
            local_detect.devinfo()
            local_detect.detect(fpath)
            local_detect.debug()
        # if os.path.splitext(opath)[-1] == ".json":
        #     local_detect.out2json(fpath=opath)
        # else:
        #     print('Visualizing result...')
        #     dpi_x: int = dpi
        #     dpi_y: int = dpi
        #     print("Size: %d, %d\nDPI: %d, %d" % (width, height, dpi_x, dpi_y))
        #     local_detect.display(None, (width/dpi_x, height/dpi_y), fpath=opath)

def clientGUI():
    from PyQt5.QtWidgets import QApplication, QStyleFactory
    from mainw import ClientGUI
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    w = ClientGUI()
    sys.exit(app.exec_())

def entry():
    preparser = argparse.ArgumentParser(add_help=False)
    preparser.add_argument('--gui', action='store_true')
    preparser.add_argument('--local', action='store_true')
    args_parsered, args_rest = preparser.parse_known_intermixed_args()  # GUI 确认后交给下一解析器
    if args_parsered.gui:
        clientGUI()
        return

    if args_parsered.local:
        parser = argparse.ArgumentParser(
            description='Client for Tensorflow Serving of Mask RCNN',
            epilog='使用例：./tf_detection.py --local --out ./output.jpg ./input.png')
    else:
        parser = argparse.ArgumentParser(
            description='Client for Tensorflow Serving of Mask RCNN (local mode)',
            epilog='使用例：./tf_detection.py --out ./output.jpg 127.0.0.1 ./input.png')
        parser.add_argument('host', metavar='(DOMAIN|IP)', help='服务器域名或 IP')
        parser.add_argument('-p', '--port', metavar='PORT',
                            default='8500', help='通信端口（默认：8500）')

    parser.add_argument('--local', action='store_true',
                        help='本地检测模式（默认：客户端模式）')
    parser.add_argument('--gui', action='store_true',
                        help='启动图形界面（将忽略所有命令行参数）')
    parser.add_argument('file', metavar='FILE', help='待处理的图像文件路径')
    parser.add_argument('-o', '--out', metavar='OUTPUT',
                        default=None, help='处理后的图像文件输出路径（不指定则输出到屏幕）')
    parser.add_argument('--width', metavar='PIXEL', type=int,
                        default=1920, help='输出图像的宽度（像素，默认:1920）')
    parser.add_argument('--height', metavar='PIXEL', type=int,
                        default=1080, help='输出图像的高度（像素，默认:1080）')
    parser.add_argument('--dpi', metavar='DPI', type=int,
                        default=96, help='输出图像的DPI（默认:96）')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='打印调试信息')
    args = parser.parse_intermixed_args()
    global IS_DEBUG; IS_DEBUG = args.verbose

    if args.out:
        opath = os.path.abspath(args.out)
    else:
        opath = None

    if args.local:
        clientCLI(os.path.abspath(args.file), opath=opath, width=args.width, height=args.height, dpi=args.dpi)
    else:
        clientCLI(os.path.abspath(args.file), args.host + ':' + args.port, opath, args.width, args.height, args.dpi)

if __name__ == '__main__':
    entry()
