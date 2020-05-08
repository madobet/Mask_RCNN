# -*- coding: UTF-8 -*-
# import os
# import sys
# import random
# import time
# import math
import numpy as np
import skimage.io

import grpc
from tensorflow_serving.apis import prediction_service_pb2_grpc
from tensorflow_serving.apis import predict_pb2
# import tensorflow as tf
from tensorflow.python.framework.tensor_util import make_tensor_proto

from mrcnn import model
from mrcnn import utils
from mrcnn import visualize
from mrcnn.model import MaskRCNN

DEFAULT_CLASS_NAMES = ['BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
                       'bus', 'train', 'truck', 'boat', 'traffic light',
                       'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
                       'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
                       'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                       'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
                       'kite', 'baseball bat', 'baseball glove', 'skateboard',
                       'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                       'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                       'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                       'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                       'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
                       'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
                       'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
                       'teddy bear', 'hair drier', 'toothbrush']

DEFAULT_CLASS_NAMES_CN = ['BG', '人', '单车', '汽车', '摩托', '飞机',
                          '公交', '火车', '卡车', '船', '信号灯',
                          '消防栓', '停车标志', '停车计时器', '板凳', '鸟',
                          '猫', '狗', '马', '羊', '牛', '大象', '熊',
                          '斑马', '长颈鹿', '背包', '雨伞', '手提包', '领带',
                          '手提箱', '飞盘', '双板滑雪板', '单板滑雪板', '球',
                          '风筝', '棒球棒', '棒球手套', '滑板',
                          '冲浪板', '网球拍', '瓶子', '酒杯', '茶杯',
                          '叉子', '刀子', '勺子', '碗', '香蕉', '苹果',
                          '三明治', '橙子', '花椰菜', '胡萝卜', '热狗', '披萨',
                          '甜甜圈', '蛋糕', '椅子', '沙发', '盆栽', '床',
                          '餐桌', '厕所', '电视', '笔记本电脑', '鼠标', '遥控器',
                          '键盘', '手机', '微波炉', '烤箱', '烤面包机',
                          '水槽', '冰箱', '书', '钟', '花盆', '剪刀',
                          '泰迪熊', '电吹风', '牙刷']

# from samples.coco.coco import CocoConfig # Requires pycocotools
from mrcnn.config import CocoConfig

class InferenceConfig(CocoConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    # def __init__(self, gpu_n=1, img_per_gpu=1):
    #     self.GPU_COUNT = gpu_n
    #     self.IMAGES_PER_GPU = img_per_gpu

class MaskRCNNClient():
    # TODO 重构成继承 MaskRCNN 类
    def __init__(self, host, class_names=DEFAULT_CLASS_NAMES_CN):
        """ host 格式 ip/domain:port
        """
        self.class_names = class_names
        # print('TF Serving server:', self.hostname)
        self.cococonfig = InferenceConfig()

        channel = grpc.insecure_channel(host, options=[(
            'grpc.max_receive_message_length', 4096 * 4096 * 3)])
        self.stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

    def img_preprocess(self, img):
        """Pre-processes the input image.
        img: Input image of shape (-1,XX,YY,3)
        Returns:
        molded_image: Molded imimg_age to be used as model input
        image_meta: Input image metadata
        anchors: [N, (y1, x1, y2, x2)]. All generated anchors in one array. Sorted
            with the same order of the given scales. So, anchors of scale[0] come
            first, then anchors of scale[1], and so on.
        window: (y1, x1, y2, x2). If max_dim is provided, padding might
            be inserted in the returned image. If so, this window is the
            coordinates of the image part of the full image (excluding
            the padding). The x2, y2 pixels are not included.
        """
        molded_image, window, scale, padding, crop = utils.resize_image(
            img,
            min_dim=self.cococonfig.IMAGE_MIN_DIM,
            min_scale=self.cococonfig.IMAGE_MIN_SCALE,
            max_dim=self.cococonfig.IMAGE_MAX_DIM,
            mode=self.cococonfig.IMAGE_RESIZE_MODE
        )
        molded_image = model.mold_image(molded_image, self.cococonfig)

        image_meta = model.compose_image_meta(
            0, img.shape, molded_image.shape, window, scale,
            np.zeros([self.cococonfig.NUM_CLASSES], dtype=np.int32)
        )

        anchors = MaskRCNN('inference', self.cococonfig,
                           None).get_anchors(molded_image.shape)
        return molded_image, image_meta, anchors, window

    def img_transform(self, image, pad_width=400, pad_value=0):
        """Resizes and/or pads the input image.
        image: Input image
        pad_width: number of pixels to pad each image vertice with
        pad_value: The value with which to pad the image (0 to 255)
        """
        image = np.pad(
            image,
            mode='constant',
            constant_values=pad_value,
            pad_width=((pad_width, pad_width), (pad_width, pad_width), (0, 0)))

        image = skimage.transform.resize(
            image,
            (self.cococonfig.IMAGE_MAX_DIM, self.cococonfig.IMAGE_MAX_DIM),
            anti_aliasing=True,
            preserve_range=True).astype(np.uint8)

        return image

    def unmold_detections(self, detections, mrcnn_mask, original_image_shape,
                          image_shape, window):
        """Reformats the detections of one image from the format of the neural
        network output to a format suitable for use in the rest of the
        application.

        detections: [N, (y1, x1, y2, x2, class_id, score)] in normalized coordinates
        mrcnn_mask: [N, height, width, num_classes]
        original_image_shape: [H, W, C] Original image shape before resizing
        image_shape: [H, W, C] Shape of the image after resizing and padding
        window: [y1, x1, y2, x2] Pixel coordinates of box in the image where the real
                image is excluding the padding.

        Returns:
        boxes: [N, (y1, x1, y2, x2)] Bounding boxes in pixels
        class_ids: [N] Integer class IDs for each bounding box
        scores: [N] Float probability scores of the class_id
        masks: [height, width, num_instances] Instance masks
        """

        # reshape tf serving output
        # the number '6' correspond to bbox coordinates (4) + class_id (1) + class confidence (1)
        detections = detections.reshape(
            -1, *(self.cococonfig.BATCH_SIZE, self.cococonfig.MAX_GT_INSTANCES, 6))
        mrcnn_mask = mrcnn_mask.reshape(-1, *(self.cococonfig.BATCH_SIZE, self.cococonfig.MAX_GT_INSTANCES,
                                              self.cococonfig.MASK_SHAPE[0], self.cococonfig.MASK_SHAPE[1], self.cococonfig.NUM_CLASSES))

        # How many detections do we have?
        # Detections array is padded with zeros. Find the first class_id == 0.
        zero_ix = np.where(detections[:, :, :, 4] == 0)[2]
        N = zero_ix[0] if zero_ix.shape[0] > 0 else detections.shape[0]

        # Extract boxes, class_ids, scores, and class-specific masks
        boxes = detections[0, 0, :N, :4]
        class_ids = detections[0, 0, :N, 4].astype(np.int32)
        scores = detections[0, 0, :N, 5]
        masks = mrcnn_mask[0, 0, np.arange(N), :, :, class_ids]

        # Translate normalized coordinates in the resized image to pixel
        # coordinates in the original image before resizing
        window = utils.norm_boxes(window, image_shape[:2])
        wy1, wx1, wy2, wx2 = window
        shift = np.array([wy1, wx1, wy1, wx1])
        wh = wy2 - wy1  # window height
        ww = wx2 - wx1  # window width
        scale = np.array([wh, ww, wh, ww])
        # Convert boxes to normalized coordinates on the window
        boxes = np.divide(boxes - shift, scale)
        # Convert boxes to pixel coordinates on the original image
        boxes = utils.denorm_boxes(boxes, original_image_shape[:2])

        # Filter out detections with zero area. Happens in early training when
        # network weights are still random
        exclude_ix = np.where(
            (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1]) <= 0)[0]
        if exclude_ix.shape[0] > 0:
            boxes = np.delete(boxes, exclude_ix, axis=0)
            class_ids = np.delete(class_ids, exclude_ix, axis=0)
            scores = np.delete(scores, exclude_ix, axis=0)
            masks = np.delete(masks, exclude_ix, axis=0)
            N = class_ids.shape[0]

        # Resize masks to original image size and set boundary threshold.
        full_masks = []
        for i in range(N):
            # Convert neural network mask to full size mask
            full_mask = utils.unmold_mask(
                masks[i, :, :], boxes[i, :], original_image_shape)
            full_masks.append(full_mask)
        full_masks = np.stack(full_masks, axis=-1)\
            if full_masks else np.empty(original_image_shape[:2] + (0,))

        return boxes, class_ids, scores, full_masks


    def grpc_request(self, img_path):
        """ 向服务器发起请求并将返回结果存放于 MaskRCNNClient 类中
        """
        self.image = skimage.io.imread(img_path)
        # self.image = self.img_transform(image, pad_width = 200)
        # plt.imshow(self.image)
        # 图像预处理
        molded_image, image_meta, anchors, window = self.img_preprocess(
            self.image)

        # proto 里定义了一种 PredictRequest message，对其进行装填
        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'mrcnn_coco'
        request.model_spec.signature_name = 'serving_default'
        np.expand_dims(self.image, axis=0)

        request.inputs['input_image'].CopyFrom(
            # tf.make_tensor_proto(np.expand_dims(molded_image, axis=0), shape=np.expand_dims(molded_image, axis=0).shape, dtype="float32"))
            make_tensor_proto(np.expand_dims(molded_image, axis=0), shape=np.expand_dims(molded_image, axis=0).shape,
                             dtype="float32"))
        request.inputs['input_image_meta'].CopyFrom(
            # tf.make_tensor_proto(np.expand_dims(image_meta, axis=0), shape=np.expand_dims(image_meta, axis=0).shape, dtype="float32"))
            make_tensor_proto(np.expand_dims(image_meta, axis=0), shape=np.expand_dims(image_meta, axis=0).shape,
                             dtype="float32"))
        request.inputs['input_anchors'].CopyFrom(
            # tf.make_tensor_proto(np.expand_dims(anchors, axis=0), shape=np.expand_dims(anchors, axis=0).shape, dtype="float32"))
            make_tensor_proto(np.expand_dims(anchors, axis=0), shape=np.expand_dims(anchors, axis=0).shape,
                             dtype="float32"))

        print('Uploading...')
        grpc_result = self.stub.Predict(request)
        print('Got prediction, destructuring result...')

        # Step 2
        grpc_mrcnn_detection = np.array(
            grpc_result.outputs["mrcnn_detection/Reshape_1"].float_val)
        grpc_mrcnn_mask = np.array(
            grpc_result.outputs["mrcnn_mask/Reshape_1"].float_val)
        grpc_rois, grpc_class_ids, grpc_scores, grpc_masks = \
            self.unmold_detections(
                grpc_mrcnn_detection, grpc_mrcnn_mask, self.image.shape, molded_image.shape, window)

        self.rois = grpc_rois
        self.class_ids = grpc_class_ids
        self.scores = grpc_scores
        self.masks = grpc_masks

    def display(self, title=None, figsize=(16, 16), axes=None, show_mask=True, show_bbox=True, show_label=True, fpath=None):
        """ 当 fpath 为 None 新开窗口显示结果
            不为 None 则保存处理后的图像到指定位置
            figsize 单位是英寸
        """
        # colors = None, captions = None, save_path = None
        if axes:
            axes.cla()
        visualize.display_instances(self.image, self.rois, self.masks, self.class_ids, self.class_names,
                                    self.scores, title, figsize, axes, show_mask, show_bbox, show_label,
                                    save_path=fpath)

    def debug(self):
        """ 打印调试信息
        """
        self.cococonfig.display()
        print('class names:', self.class_names)
        print('ROIs:', self.rois)
        print('class IDs:', self.class_ids)
        print('scores:', self.scores)
        print('masks:', self.masks)
