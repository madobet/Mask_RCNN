#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os
from concurrent import futures
import time
import math
import logging

import grpc
# from PIL import Image
# import io

import apis.route_tf_pb2
import apis.route_tf_pb2_grpc

import mrcnn_demo_local
import skimage.io

ROOT_DIR = os.path.abspath("../")
# IMAGE_DIR = os.path.join(ROOT_DIR, "images")
IMAGE_DIR = os.path.join(ROOT_DIR, "just4fun")
print(IMAGE_DIR)


def get_feature(request):
    # io + Pillow 读入 Pillow 的 Image 对象
    # img = Image.open(io.BytesIO(request.data))

    # img = skimage.io.imread(os.path.join(IMAGE_DIR,os.path.join(IMAGE_DIR, file_name)))
    print(request.filename)
    img = skimage.io.imread(request.data, plugin='imageio', format='jpg')

    skimage.io.imsave("success.jpg", img, format='jpg')
    # results = mask_rcnn_demo.detection(img)
    image = skimage.io.imread("test.jpg")
    # mask_rcnn_demo.detection(image)

    # 如果要 batch 处理，只需要把单张图片组成一个 list 即可：
    # imgs = []
    # imgs.append(img)

    # TODO 支持多张图批量
    # for i in range(len(results)):
    #     mask.append(wrapper_result(results[i]))

    mask = route_tf_pb2.Mask(filename=request.filename)
    # r = results[0]
    # # ROIs
    # r_rois = r['rois']
    # for roi in r_rois:
    #     msg_roi = route_tf_pb2.Roi(
    #         leftup=route_tf_pb2.Point(x=roi[1], y=roi[0]),
    #         rightbottom=route_tf_pb2.Point(x=roi[3], y=roi[2]))
    #     mask.rois.append(msg_roi)
    # # Class IDs
    # mask.class_id.extend(r['class_ids'])
    # # Scores
    # mask.scores.extend(r['scores'])
    # # Mask
    # for row in r['masks']:
    #     msg_maskrow = route_tf_pb2.MaskRow()
    #     for pixel_bools in row:
    #         msg_pixeltype = route_tf_pb2.PixelType(belongs=pixel_bools)
    #         msg_maskrow.pixeltypes.append(msg_pixeltype)
    #     mask.mask.append(msg_maskrow)
    return mask


class RouteTFServicer(route_tf_pb2_grpc.RouteTFServicer):

    def GetFeature(self, request, context):
        return get_feature(request)

    def RecordRoute(self, request_iterator, context):
        return get_feature(request)

    def RouteChat(self, request_iterator, context):
        prev_notes = []
        for new_note in request_iterator:
            for prev_note in prev_notes:
                if prev_note.location == new_note.location:
                    yield prev_note
            prev_notes.append(new_note)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    route_tf_pb2_grpc.add_RouteTFServicer_to_server(
        RouteTFServicer(), server)
    server.add_insecure_port('[::]:50050')
    server.start()
    print("Server started!")
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
