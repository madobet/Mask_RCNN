# -*- coding: UTF-8 -*-
import os
import skimage.io

from mrcnn import utils, visualize
import mrcnn.model as modellib

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

class MaskRCNNLocal():
    # TODO 重构成继承 MaskRCNN 类
    def __init__(self, gpu_n=1, class_names=DEFAULT_CLASS_NAMES_CN):
        """ 给出图像读取路径
        """
        self.class_names = class_names

        self.cococonfig = CocoConfig()
        self.cococonfig.GPU_COUNT = gpu_n

        work_path = os.path.abspath("./")
        # Directory to save logs and trained model
        self.model_dir = os.path.join(work_path, "logs")
        # Local path to trained weights file
        self.coco_model_path = os.path.join(work_path, "keras_model/mask_rcnn_coco.h5")

        # NOTE batch 模式因为图片总数不定每次都需要重新创建 MaskRCNN 类，效率低下，只适合于训练
        # self.img_path = img_path
        # print(self.img_path)
        # if os.path.isdir(self.img_path):
        #     images_per_gpu = len(os.listdir(self.img_path))
        # else:
        #     images_per_gpu = 1
        self.cococonfig.IMAGES_PER_GPU = 1
        self.cococonfig.BATCH_SIZE = self.cococonfig.GPU_COUNT * self.cococonfig.IMAGES_PER_GPU

        # Download COCO trained weights from Releases if needed
        if not os.path.exists(self.coco_model_path):
            utils.download_trained_weights(self.coco_model_path)

        # Create model object in inference mode
        self.model = modellib.MaskRCNN(mode="inference", model_dir=self.model_dir, config=self.cococonfig)

        # Load weights trained on MS-COCO
        print("Loading weights...")
        self.model.load_weights(self.coco_model_path, by_name=True)
        print(self.model.keras_model, "loaded")

    def devinfo(self):
        """ Check devices info
        :return:
        """
        import tensorflow as tf

        print("[CUDA support]>>>", tf.test.is_built_with_cuda())
        print("[GPU support]>>>", tf.test.is_built_with_gpu_support())
        print("[ROCm (GPU) support]>>>", tf.test.is_built_with_rocm())

        physical_devices = tf.config.list_physical_devices('GPU')
        # print("[GPU info]>>>", physical_devices)
        if physical_devices:
            tf.config.experimental.set_memory_growth(physical_devices[0], True)

        from tensorflow.python.client import device_lib
        print("[Details]>>>\n", device_lib.list_local_devices())

    def detect(self, img_path):
        self.images = []
        if os.path.isdir(img_path):
            for file in os.listdir(img_path):
                self.images.append(skimage.io.imread(os.path.join(img_path, file)))
        else:
            self.images.append(skimage.io.imread(img_path))

        # Run detection
        # self.results = self.model.detect(self.images, verbose=1)
	    self.results = self.model.detect(self.images, verbose=0)

    def display(self, title=None, figsize=(16, 16), axes=None, show_mask=True, show_bbox=True, show_label=True, fpath=None):
        """ 当 fpath 为 None 新开窗口显示结果
            不为 None 则保存处理后的图像到指定位置
            figsize 单位是英寸
        """
        # colors = None, captions = None, save_path = None
        if axes:
            axes.cla()
        # Visualize results
        for i in range(len(self.images)):
            r = self.results[i]
            visualize.display_instances(self.images[i], r['rois'], r['masks'], r['class_ids'], self.class_names,
                                    r['scores'], title, figsize, axes, show_mask, show_bbox, show_label,
                                    save_path=fpath)

    def debug(self):
        """ 打印调试信息
        """
        self.cococonfig.display()
        print('class names:', self.class_names)
