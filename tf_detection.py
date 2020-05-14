#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os, sys, argparse

# plot format
from typing import Dict, Any

from matplotlib import rcParams
rcParams['font.family'] = ['sans-serif']
rcParams['font.weight'] = 'semibold'
rcParams['font.size'] = 20
rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'SimHei', 'sans', 'sans-serif']
# rcParams['axes.unicode_minus'] = False

# NOTE 如果出现中文字体找不到或显示异常，可尝试删除 ~/.cache/matplotlib 缓存
from matplotlib.font_manager import _rebuild
_rebuild()

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

args: Dict[Any, Any] = None
model_obj = None

import socket, selectors, types

def model_initial(host=None):
    global args
    if host:
        if args.verbose > 0:
            print("creating client class connected to:", host)
        from mrcnn.model_client import MaskRCNNClient
        return MaskRCNNClient(host)
    else:
        if args.verbose > 0:
            print("creating local model class...")
        from mrcnn.model_local import MaskRCNNLocal
        model = MaskRCNNLocal()
        if args.verbose > 1:
            model.devinfo()
        return model

def clientCLI(in_path, out_path=None):
    global args
    global model_obj

    # 输入输出路径预处理
    in_path = os.path.abspath(in_path.strip())
    out_path = os.path.abspath(out_path.strip())
    if args.verbose > 0:
        print("input:", in_path, "output:", out_path)
    if not os.access(in_path, os.R_OK):
        return in_path + ' does not existed, or unreadable'
    elif os.path.exists(out_path) and (not os.access(out_path, os.W_OK)):
        return out_path + ' unwritable'

    # 调用模型检测
    if args.verbose > 0:
        print("calling model:", type(model_obj))
    model_obj.detect(in_path, args.verbose - 1)

    # 输出结果
    if args.verbose > 1:
        model_obj.debug()
    if os.path.splitext(out_path)[-1] == ".json":
        model_obj.out2json(opath=out_path)
    else:
        if args.verbose > 0:
            print('visualizing result...')
        dpi_x: int = args.dpi
        dpi_y: int = args.dpi
        if args.verbose > 1:
            print("size: %d, %d\ndpi: %d, %d" % (args.width, args.height, dpi_x, dpi_y))
        model_obj.display(None, (args.width / dpi_x, args.height / dpi_y), fpath=out_path)
    return 'result saved to ' + out_path

def accept_wrapper(sersock):
    # 由于监听 serversock 被注册到了 selectors.EVENT_READ 上，它现在就能被读取，
    # 调用 sersock.accept() 后立即再立即调 clientsock.setblocking(False)
    # 来让 client 的 socket 也进入非阻塞模式？
    (clientsock, clientaddr) = sersock.accept()  # Should be ready to read
    print('connection:', clientsock, 'established from:', clientaddr)
    clientsock.setblocking(False)
    # 欢迎语
    msg = 'Welcome to ' + clientsock.getsockname()[0] + ' !'
    clientsock.send(str.encode(msg))
    data = types.SimpleNamespace(addr=clientaddr, inb=b'', outb=b'')
    # 接着我们使用了 types.SimpleNamespace 类创建了一个对象用来保存我们想要的
    # socket 和数据，由于我们得知道客户端连接什么时候可以写入或者读取，下面两个事件都
    # 会被用到：
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(clientsock, events, data=data)

def service_connection(key, mask):
    global args
    # 处理客户端 socket 就绪时的连接请求
    clientsock = key.fileobj
    data = key.data
    # key  就是从调用 select() 方法返回的一个具名元组
    #      包含了 socket 对象「fileobj」和数据对象
    # mask 包含了就绪的事件
    if mask & selectors.EVENT_READ:
        # 如果 socket 就绪而且可以被读取，mask & selectors.EVENT_READ 就为真
        recv_data = clientsock.recv(1024)  # Should be ready to read
        if recv_data:
            # 所有读取到的数据都会被追加到 data.outb 里面。随后被发送出去
            data.outb += recv_data
            if args.verbose > 0:
                print('received:', data.outb.decode(), 'from:', data.addr)  # 打印接收到的数据
            in_path, out_path = data.outb.decode().split(';')
            response_msg = clientCLI(in_path, out_path)
            if args.verbose > 0:
                print(response_msg)

        else:
            print('connection closed:', data.addr)
            # 别忘了先调用 sel.unregister() 撤销 select() 的监控
            sel.unregister(clientsock)
            clientsock.close()  # 服务端也应关闭自己的连接
        if mask & selectors.EVENT_WRITE:
            # 当 socket 就绪而且可以被写入时，对于正常的 socket 应该一直是这种状态，
            # 任何接收并被 data.outb 存储的数据都将使用 sock.send() 方法打印出来。
            if data.outb:
                if args.verbose > 0:
                    print('sending response to client...')
                if out_path:
                    sent_data = clientsock.send(str.encode(response_msg))
                data.outb = data.outb[sent_data:]  # 从缓冲中删除发送出的字节
                # while sent_data = clientsock.sendall(data):
                #     print('SENDING DATA...')
                if args.verbose > 0:
                    print('finished')

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
    preparser.add_argument('-d', '--daemon', action='store_true')
    args_parsered, args_rest = preparser.parse_known_intermixed_args()  # GUI 确认后交给下一解析器
    if args_parsered.gui:
        clientGUI()
        return

    if args_parsered.local and args_parsered.daemon:
        parser = argparse.ArgumentParser(
            description='Client for Tensorflow Serving of Mask RCNN (local-daemon mode)',
            epilog='使用例：./tf_detection.py --local --daemon --out ./output.jpg ./input.png')
    elif args_parsered.local and not args_parsered.daemon:
        parser = argparse.ArgumentParser(
            description='Client for Tensorflow Serving of Mask RCNN (local mode)',
            epilog='使用例：./tf_detection.py --local --out ./output.jpg ./input.png')
        parser.add_argument('file', metavar='FILE', help='待处理的图像文件路径')
    elif not args_parsered.local and args_parsered.daemon:
        parser = argparse.ArgumentParser(
            description='Client for Tensorflow Serving of Mask RCNN (daemon mode)',
            epilog='使用例：./tf_detection.py --daemon --out ./output.jpg 127.0.0.1 ./input.png')
        parser.add_argument('host', metavar='(DOMAIN|IP)', help='服务器域名或 IP')
        parser.add_argument('-p', '--port', metavar='PORT',
                            default='8500', help='通信端口（默认：8500）')
    else:
        parser = argparse.ArgumentParser(
            description='Client for Tensorflow Serving of Mask RCNN',
            epilog='使用例：./tf_detection.py --out ./output.jpg 127.0.0.1 ./input.png')
        parser.add_argument('host', metavar='(DOMAIN|IP)', help='服务器域名或 IP 地址')
        parser.add_argument('-p', '--port', metavar='PORT',
                            default='8500', help='通信端口（默认：8500）')
        parser.add_argument('file', metavar='FILE', help='待处理的图像文件路径')


    parser.add_argument('--local', action='store_true',
                        help='本地模式（默认客户端模式）')
    parser.add_argument('--gui', action='store_true',
                        help='启动图形界面（所有命令行参数都将失效）')
    parser.add_argument('-o', '--out', metavar='OUTPUT',
                        default=None, help='处理后的图像文件输出路径（不指定则输出到屏幕）')
    parser.add_argument('--width', metavar='PIXEL', type=int,
                        default=1920, help='输出图像的宽度（单位：px，默认：1920）')
    parser.add_argument('--height', metavar='PIXEL', type=int,
                        default=1080, help='输出图像的高度（单位：px，默认：1080）')
    parser.add_argument('--dpi', metavar='DPI', type=int,
                        default=96, help='输出图像的DPI（默认:96）')
    parser.add_argument('-d', '--daemon', action='store_true',
                        help='启用 Socket 监听（注：如果传递的数据中包含中文，必须使用 UTF-8 编码）')
    parser.add_argument('--sockip', metavar='IP',
                        default='127.0.0.1', help='Socket 监听地址（默认：127.0.0.1）')
    parser.add_argument('--sockport', metavar='PORT', type=int,
                        default=8912, help='Socket 监听端口（默认：8912）')
    parser.add_argument('-v', '--verbose', action='count',
                        default=0, help='调试等级，可多次指定')
    global args; args = parser.parse_intermixed_args()
    if args.out:
        args.out = os.path.abspath(args.out)
    else:
        args.out = None

    global model_obj
    if args.local:
        model_obj = model_initial()
    else:
        model_obj = model_initial(args.host + ':' + args.port)

    if args.daemon:
        if args.verbose > 0:
            print('launching socket server...')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversock:
            serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serversock.bind((args.sockip, args.sockport))
            serversock.listen(5)  # become a server socket
            print('listening on:', (args.sockip, args.sockport))
            serversock.setblocking(False)
            sel.register(serversock, selectors.EVENT_READ, data=None)

            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)
    else:
        clientCLI(args.file, args.out)

if __name__ == '__main__':
    sel = selectors.DefaultSelector()
    entry()
