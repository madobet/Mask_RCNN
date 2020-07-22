using System;
using System.Collections.Generic;
using System.Linq;
using System.Security;
using System.Text;
using System.Threading.Tasks;

namespace Mask_RCNN_cashrp
{
    class Config
    {
        protected string NAME = "default";
        string Name
        {
            set
            {
                // TODO 检查名称是否合法
                NAME = value;
            }
            get
            {
                return NAME;
            }
        }

        protected int GPU_COUNT;
        int GpuCount
        {
            set
            {
                // TODO 检查是否大于 0 否则 等于 0 则禁用 GPU 小于 0 则报错
                GPU_COUNT = value;
            }
            get
            {
                return GPU_COUNT;
            }
        }

        protected int IMAGES_PER_GPU;
        int ImagesPerGpu
        {
            set
            {
                // TODO 检查是否大于 0 否则报错
                IMAGES_PER_GPU = value;
            }
            get
            {
                return IMAGES_PER_GPU;
            }
        }

        private int STEPS_PER_EPOCH = 1000;
        int StepsPerEpoch
        {
            set
            {
                // Number of training steps per epoch
                // This doesn't need to match the size of the training set. Tensorboard
                // updates are saved at the end of each epoch, so setting this to a
                // smaller number means getting more frequent TensorBoard updates.
                // Validation stats are also calculated at each epoch end and they
                // might take a while, so don't set this too small to avoid spending
                // a lot of time on validation stats.
                STEPS_PER_EPOCH = value;
            }
            get
            {
                return STEPS_PER_EPOCH;
            }
        }

        int VALIDATION_STEPS = 50;
        int ValidationSteps
        {
            set
            {
                // Number of validation steps to run at the end of every training epoch.
                // A bigger number improves accuracy of validation stats, but slows
                // down the training.
                VALIDATION_STEPS = value;
            }
            get
            {
                return VALIDATION_STEPS;
            }
        }

        protected string BACKBONE = "resnet101";
        string Backbone
        {
            set
            {
                // Backbone network architecture
                // Supported values are: resnet50, resnet101.
                // You can also provide a callable that should have the signature
                // of model.resnet_graph. If you do so, you need to supply a callable
                // to COMPUTE_BACKBONE_SHAPE as well
                BACKBONE = value;
            }
            get
            {
                return BACKBONE;
            }

        }

        // Only useful if you supply a callable to BACKBONE. Should compute
        // the shape of each layer of the FPN Pyramid.
        // See model.compute_backbone_shapes
        // COMPUTE_BACKBONE_SHAPE = 一个函数引用或指针（或回调）

        // The strides of each layer of the FPN Pyramid. These values
        // are based on a Resnet101 backbone.
        int[] BACKBONE_STRIDES { set; get; } = { 4, 8, 16, 32, 64 };

        private int FPN_CLASSIF_FC_LAYERS_SIZE = 1024;
        int FpnClassifFcLayersSize
        {
            set
            {
                // Size of the fully-connected layers in the classification graph
                FPN_CLASSIF_FC_LAYERS_SIZE = value;
            }
            get
            {
                return FPN_CLASSIF_FC_LAYERS_SIZE;
            }
        }

        private int TOP_DOWN_PYRAMID_SIZE = 256;
        int TopDownPyramidSize
        {
            set
            {
                // Size of the top-down layers used to build the feature pyramid
                TOP_DOWN_PYRAMID_SIZE = value;
            }
            get
            {
                return TOP_DOWN_PYRAMID_SIZE;
            }
        }

        protected int NUM_CLASSES = 1;
        int NumClasses
        {
            set
            {
                // Number of classification classes (including background)
                // Change it in sub-classes
                NUM_CLASSES = value;
            }
            get
            {
                return NUM_CLASSES;
            }
        }

        // Length of square anchor side in pixels
        int[] RPN_ANCHOR_SCALES { set; get; } = { 32, 64, 128, 256, 512 };

        // Ratios of anchors at each cell (width/height)
        // A value of 1 represents a square anchor, and 0.5 is a wide anchor
        double[] RPN_ANCHOR_RATIOS { set; get; } = { 0.5, 1, 2 };

        private int RPN_ANCHOR_STRIDE = 1;
        int RpnAnchorStride
        {
            set
            {
                // Anchor stride
                // If 1 then anchors are created for each cell in the backbone feature map.
                // If 2, then anchors are created for every other cell, and so on.
                RPN_ANCHOR_STRIDE = value;
            }
            get
            {
                return RPN_ANCHOR_STRIDE;
            }
        }

        private double RPN_NMS_THRESHOLD = 0.7;
        double RpnNmsThreshold
        {
            set
            {
                // Non-max suppression threshold to filter RPN proposals.
                // You can increase this during training to generate more propsals.
                RPN_NMS_THRESHOLD = value;
            }
            get
            {
                return RPN_NMS_THRESHOLD;
            }
        }

        private int RPN_TRAIN_ANCHORS_PER_IMAGE = 256;
        int RpnTrainAnchorsPerImage
        {
            set
            {
                // How many anchors per image to use for RPN training
                RPN_TRAIN_ANCHORS_PER_IMAGE = value;
            }
            get
            {
                return RPN_TRAIN_ANCHORS_PER_IMAGE;
            }
        }

        // ROIs kept after tf.nn.top_k and before non-maximum suppression
        private int PRE_NMS_LIMIT = 6000;

        // ROIs kept after non-maximum suppression (training and inference)
        private int POST_NMS_ROIS_TRAINING = 2000;
        private int POST_NMS_ROIS_INFERENCE = 1000;

        // If enabled, resizes instance masks to a smaller size to reduce
        // memory load. Recommended when using high-resolution images.
        private bool USE_MINI_MASK = true;
        private int[] MINI_MASK_SHAPE { set; get; } = { 56, 56 };  // (height, width) of the mini-mask

        private string IMAGE_RESIZE_MODE = "square";
        string ImageResizeMode
        {
            set
            {
                // Input image resizing
                // Generally, use the "square" resizing mode for training and predicting
                // and it should work well in most cases. In this mode, images are scaled
                // up such that the small side is = IMAGE_MIN_DIM, but ensuring that the
                // scaling doesn't make the long side > IMAGE_MAX_DIM. Then the image is
                // padded with zeros to make it a square so multiple images can be put
                // in one batch.
                // Available resizing modes:
                // none:   No resizing or padding. Return the image unchanged.
                // square: Resize and pad with zeros to get a square image
                //         of size [max_dim, max_dim].
                // pad64:  Pads width and height with zeros to make them multiples of 64.
                //         If IMAGE_MIN_DIM or IMAGE_MIN_SCALE are not None, then it scales
                //         up before padding. IMAGE_MAX_DIM is ignored in this mode.
                //         The multiple of 64 is needed to ensure smooth scaling of feature
                //         maps up and down the 6 levels of the FPN pyramid (2**6=64).
                // crop:   Picks random crops from the image. First, scales the image based
                //         on IMAGE_MIN_DIM and IMAGE_MIN_SCALE, then picks a random crop of
                //         size IMAGE_MIN_DIM x IMAGE_MIN_DIM. Can be used in training only.
                //         IMAGE_MAX_DIM is not used in this mode.
                // TODO 检查是否有效模式
                IMAGE_RESIZE_MODE = value;
            }
            get
            {
                return IMAGE_RESIZE_MODE;
            }
        }

        int IMAGE_MIN_DIM { set; get; } = 800;
        int IMAGE_MAX_DIM { set; get; } = 1024;
        // Minimum scaling ratio. Checked after MIN_IMAGE_DIM and can force further
        // up scaling. For example, if set to 2 then images are scaled up to double
        // the width and height, or more, even if MIN_IMAGE_DIM doesn't require it.
        // However, in 'square' mode, it can be overruled by IMAGE_MAX_DIM.
        int IMAGE_MIN_SCALE { set; get; } = 0;

        private int IMAGE_CHANNEL_COUNT = 3;
        int ImageChannelCount
        {
            set
            {
                // Number of color channels per image. RGB = 3, grayscale = 1, RGB-D = 4
                // Changing this requires other changes in the code. See the WIKI for more
                // details: https://github.com/matterport/Mask_RCNN/wiki
                // TODO 三种不同的条件作判断
                IMAGE_CHANNEL_COUNT = value;
            }
            get
            {
                return IMAGE_CHANNEL_COUNT;
            }
        }

        // Image mean (RGB)
        //double[] MEAN_PIXEL { set; get; } = np.array({123.7, 116.8, 103.9});

        private int TRAIN_ROIS_PER_IMAGE = 200;
        int TrainRoisPerImage
        {
            set
            {
                // Number of ROIs per image to feed to classifier/mask heads
                // The Mask RCNN paper uses 512 but often the RPN doesn't generate
                // enough positive proposals to fill this and keep a positive:negative
                // ratio of 1:3. You can increase the number of proposals by adjusting
                // the RPN NMS threshold.
                TRAIN_ROIS_PER_IMAGE = value;
            }
            get
            {
                return TRAIN_ROIS_PER_IMAGE;
            }
        }

        // Percent of positive ROIs used to train classifier/mask heads
        private double ROI_POSITIVE_RATIO = 0.33;
        double RoiPositiveRatio
        {
            set
            {
                ROI_POSITIVE_RATIO = value;
            }
            get
            {
                return ROI_POSITIVE_RATIO;
            }
        }

        private int POOL_SIZE = 7;
        int PoolSize
        {
            set
            {
                // Pooled ROIs
                POOL_SIZE = value;
            }
            get
            {
                return POOL_SIZE;
            }
        }
        private int MASK_POOL_SIZE = 14;
        int MaskPoolSize
        {
            set
            {
                // Pooled ROIs
                MASK_POOL_SIZE = value;
            }
            get
            {
                return MASK_POOL_SIZE;
            }
        }

        // Shape of output mask
        // To change this you also need to change the neural network mask branch
        int[] MASK_SHAPE { set; get; } = { 28, 28 };

        private int MAX_GT_INSTANCES = 100;
        int MaxGtInstances
        {
            set
            {
                // Maximum number of ground truth instances to use in one image
                MAX_GT_INSTANCES = value;
            }
            get
            {
                return MAX_GT_INSTANCES;
            }
        }

        // Bounding box refinement standard deviation for RPN and final detections.
        //double[] RPN_BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2]);
        //BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2]);

        private int DETECTION_MAX_INSTANCES = 100;
        int DetectionMaxInstances {
            set
            {
                // Max number of final detections
                DETECTION_MAX_INSTANCES = value;
            }
            get
            {
                return DETECTION_MAX_INSTANCES;
            }
        }


        private double DETECTION_MIN_CONFIDENCE = 0.7;
        double DetectionMinConfidence
        {
            set
            {
                // Minimum probability value to accept a detected instance
                // ROIs below this threshold are skipped
                DETECTION_MIN_CONFIDENCE = value;
            }
            get
            {
                return DETECTION_MIN_CONFIDENCE;
            }
        }

        private double DETECTION_NMS_THRESHOLD = 0.3;
        double DetectionNmsThreshold
        {
            set
            {
                // Non-maximum suppression threshold for detection
                DETECTION_NMS_THRESHOLD = value;
            }
            get
            {
                return DETECTION_NMS_THRESHOLD;
            }
        }

        // Learning rate and momentum
        // The Mask RCNN paper uses lr=0.02, but on TensorFlow it causes
        // weights to explode. Likely due to differences in optimizer
        // implementation.
        public readonly double LEARNING_RATE = 0.001;
        public readonly double LEARNING_MOMENTUM = 0.9;

        // Weight decay regularization
        public readonly double WEIGHT_DECAY = 0.0001;

        // Loss weights for more precise optimization.
        // Can be used for R-CNN training setup.
        // 嵌套类可以访问外部类的方法、属性、字段而不管访问修饰符的限制。
        // 但是外部类只能够访问修饰符为public、internal嵌套类的字段、方法、属性。
        struct loss_weight {
            public double rpn_class_loss;
            public double rpn_bbox_loss;
            public double mrcnn_class_loss;
            public double mrcnn_bbox_loss;
            public double mrcnn_mask_loss;
        }
        loss_weight LOSS_WEIGHTS;


        // Use RPN ROIs or externally generated ROIs for training
        // Keep this True for most situations. Set to False if you want to train
        // the head branches on ROI generated by code rather than the ROIs from
        // the RPN. For example, to debug the classifier head without having to
        // train the RPN.
        private bool USE_RPN_ROIS = true;
        bool UseRpnRois
        {
            set
            {
                USE_RPN_ROIS = value;
            }
            get
            {
                return USE_RPN_ROIS;
            }
        }

        private bool TRAIN_BN = false;  // Defaulting to false since batch size is often small
        bool TrainBn
        {
            set
            {
                // Train or freeze batch normalization layers
                // None: Train BN layers. This is the normal mode
                // False: Freeze BN layers. Good when using a small batch size
                // True: (don't use). Set layer in training mode even when predicting
                TRAIN_BN = value;
            }
            get
            {
                return TRAIN_BN;
            }
        }

        private double GRADIENT_CLIP_NORM = 5.0;
        double GradientClipNorm
        {
            set
            {
                // Gradient norm clipping
                GRADIENT_CLIP_NORM = value;
            }
            get
            {
                return GRADIENT_CLIP_NORM;
            }
        }

        int BatchSize
        {
            // Effective batch size
            get
            {
                return IMAGES_PER_GPU * GPU_COUNT;
            }
        }

        np_array ImageShape
        {
            get
            {
                // Input image size
                if (IMAGE_RESIZE_MODE == "crop")
                {
                    return np.array([IMAGE_MIN_DIM, IMAGE_MIN_DIM, IMAGE_CHANNEL_COUNT]);
                }
                else
                {
                    return np.array([IMAGE_MAX_DIM, IMAGE_MAX_DIM, IMAGE_CHANNEL_COUNT]);
                }
            }
        }

        int ImageMetaSize
        {
            get
            {
                // Image meta data length
                // See compose_image_meta() for details
                return 1 + 3 + 3 + 4 + 1 + NUM_CLASSES;
            }
        }

        public Config()
        {
            LOSS_WEIGHTS.rpn_class_loss = 1;
            LOSS_WEIGHTS.rpn_bbox_loss = 1;
            LOSS_WEIGHTS.mrcnn_class_loss = 1;
            LOSS_WEIGHTS.mrcnn_bbox_loss = 1;
            LOSS_WEIGHTS.mrcnn_mask_loss = 1;
        }

        public void Display()
        {
            // Display Configuration values
            Console.WriteLine("\nConfigurations:");
            //for a in dir(self) :
            //    if not a.startswith("__") and not callable(getattr(self, a)) :
            //        print("{:30} {}".format(a, getattr(self, a)))
            //print("\n")
        }
    }

    class CocoConfig : Config
    {
        // Configuration for training on MS COCO.CocoConfig
        // Derives from the base Config class and overrides values specific
        // to the COCO dataset.
        // Give the configuration a recognizable name
        new public readonly string NAME = "coco";

        // We use a GPU with 12GB memory, which can fit two images.
        // Adjust down if you use a smaller GPU.
        new public readonly int IMAGES_PER_GPU = 2;

        // Uncomment to train on 8 GPUs (default is 1)
        new public readonly int GPU_COUNT = 8;

        // Number of classes (including background)
        new public readonly int NUM_CLASSES = 1 + 80;  // COCO has 80 classes
    }

}
