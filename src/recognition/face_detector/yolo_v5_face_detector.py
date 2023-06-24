from skimage import transform
import numpy as np
import tensorflow as tf
import os

gpus = tf.config.experimental.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

""" Yolov5-face Ported from https://github.com/deepcam-cn/yolov5-face """


class YoloV5FaceDetector:
    default_anchors = np.array(
        [
            [[0.5, 0.625], [1.0, 1.25], [1.625, 2.0]],
            [[1.4375, 1.8125], [2.6875, 3.4375], [4.5625, 6.5625]],
            [[4.5625, 6.781199932098389], [7.218800067901611, 9.375],
             [10.468999862670898, 13.531000137329102]],
        ],
        dtype="float32",
    )

    default_strides = np.array([8, 16, 32], dtype="float32")
    default_detector = os.path.join(
        os.getcwd(), "src/models/yolo_v5/yolov5s_face_dynamic.h5")

    file_hash = {"yolov5s_face_dynamic": "e7854a5cae48ded05b3b31aa93765f0d"}
    default_detector_http = "https://github.com/leondgarse/Keras_insightface/releases/download/v1.0.0/yolov5s_face_dynamic.h5"

    def __init__(self, model_path=default_detector, anchors=default_anchors, strides=default_strides, image_size=(160, 160)):
        if isinstance(model_path, str) and model_path.startswith("http"):
            file_name = os.path.basename(model_path)
            file_hash = file_hash.get(os.path.splitext(file_name)[0], None)
            model_path = tf.keras.utils.get_file(
                file_name, model_path, cache_subdir="models", file_hash=file_hash)
            self.model = tf.keras.models.load_model(model_path)
        elif isinstance(model_path, str) and model_path.endswith(".h5"):
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = model_path

        self.anchors, self.strides = anchors, strides
        self.num_anchors = anchors.shape[1]
        self.anchor_grids = tf.math.ceil(
            (anchors * strides[:, tf.newaxis, tf.newaxis])[:, tf.newaxis, :, tf.newaxis, :])
        self.image_size = image_size

    def make_grid(self, nx=20, ny=20, dtype=tf.float32):
        xv, yv = tf.meshgrid(tf.range(nx), tf.range(ny))
        return tf.cast(tf.reshape(tf.stack([xv, yv], 2), [1, 1, -1, 2]), dtype=dtype)

    def pre_process_32(self, image):
        hh, ww, _ = image.shape
        pad_hh = (32 - hh % 32) % 32  # int(tf.math.ceil(hh / 32) * 32) - hh
        pad_ww = (32 - ww % 32) % 32  # int(tf.math.ceil(ww / 32) * 32) - ww
        if pad_ww != 0 or pad_hh != 0:
            image = tf.pad(image, [[0, pad_hh], [0, pad_ww], [0, 0]])
        return tf.expand_dims(image, 0)

    def post_process(self, outputs, image_height, image_width):
        post_outputs = []
        for output, stride, anchor, anchor_grid in zip(outputs, self.strides, self.anchors, self.anchor_grids):
            hh, ww = image_height // stride, image_width // stride
            anchor_width = output.shape[-1] // self.num_anchors
            output = tf.reshape(
                output, [-1, output.shape[1] * output.shape[2], self.num_anchors, anchor_width])
            output = tf.transpose(output, [0, 2, 1, 3])

            cls = tf.sigmoid(output[:, :, :, :5])
            cur_grid = self.make_grid(ww, hh, dtype=output.dtype) * stride
            xy = cls[:, :, :, 0:2] * (2 * stride) - 0.5 * stride + cur_grid
            wh = (cls[:, :, :, 2:4] * 2) ** 2 * anchor_grid

            mm = [1, 1, 1, 5]
            landmarks = output[:, :, :, 5:15] * \
                tf.tile(anchor_grid, mm) + tf.tile(cur_grid, mm)

            post_out = tf.concat(
                [xy, wh, landmarks, cls[:, :, :, 4:]], axis=-1)
            post_outputs.append(tf.reshape(
                post_out, [-1, output.shape[1] * output.shape[2], anchor_width - 1]))
        return tf.concat(post_outputs, axis=1)

    def yolo_nms(self, inputs, max_output_size=15, iou_threshold=0.35, score_threshold=0.25):
        inputs = inputs[0][inputs[0, :, -1] > score_threshold]
        xy_center, wh, ppt, cct = inputs[:, :2], inputs[:,
                                                        2:4], inputs[:, 4:14], inputs[:, 14]
        xy_start = xy_center - wh / 2
        xy_end = xy_start + wh
        bbt = tf.concat([xy_start, xy_end], axis=-1)
        rr = tf.image.non_max_suppression(
            bbt, cct, max_output_size=max_output_size, iou_threshold=iou_threshold, score_threshold=0.0)
        bbs, pps, ccs = tf.gather(bbt, rr, axis=0), tf.gather(
            ppt, rr, axis=0), tf.gather(cct, rr, axis=0)
        pps = tf.reshape(pps, [-1, 5, 2])
        return bbs.numpy(), pps.numpy(), ccs.numpy()

    def detect(self, image, max_output_size=15, iou_threshold=0.45, score_threshold=0.25, image_format="RGB"):
        imm_RGB = image if image_format == "RGB" else image[:, :, ::-1]
        imm_RGB = self.pre_process_32(imm_RGB)
        outputs = self.model(imm_RGB)
        post_outputs = self.post_process(
            outputs, imm_RGB.shape[1], imm_RGB.shape[2])
        return self.yolo_nms(post_outputs, max_output_size, iou_threshold, score_threshold)

    def detect_in_image(self, image, max_output_size=15, iou_threshold=0.45, score_threshold=0.25, image_format="BGR"):
        imm_RGB = image[:, :, ::-1] if image_format == "BGR" else image
        bbs, pps, ccs = self.detect(
            imm_RGB, max_output_size, iou_threshold, score_threshold, image_format="RGB")
        nimgs = self.face_align_landmarks(imm_RGB, pps)

        return bbs, pps, ccs, nimgs

    def face_align_landmarks(self, img, landmarks, method="similar"):
        tform = transform.AffineTransform(
        ) if method == "affine" else transform.SimilarityTransform()
        src = np.array([[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366], [
            41.5493, 92.3655], [70.729904, 92.2041]], dtype=np.float32)
        ret = []
        for landmark in landmarks:
            tform.estimate(landmark, src)
            img_temp = transform.warp(
                img, tform.inverse, output_shape=self.image_size)
            ret.append(img_temp)

        return (np.array(ret) * 255).astype(np.uint8)
