import numpy as np
import os
import onnxruntime as ort
import cv2
from scipy.special import softmax
from logger import logger


class FasProcessor:
    model_dir = 'src/models/fas_detection'
    model_name_v2 = "2.7_80x80_MiniFASNetV2.onnx"
    model_name_v1 = "4_0_0_80x80_MiniFASNetV1SE.onnx"

    input_std = 1.0
    input_size = (80, 80)
    input_mean = 0.0

    ort.set_default_logger_severity(0)
    providers = [
        ('CUDAExecutionProvider', {
            'device_id': 0,
            'arena_extend_strategy': 'kNextPowerOfTwo',
            'gpu_mem_limit': 1 * 1024 * 1024 * 1024,
            'cudnn_conv_algo_search': 'EXHAUSTIVE',
            'do_copy_in_default_stream': True
        }),
        "CPUExecutionProvider",
    ]

    def __init__(self):
        self._load_model_v2(os.path.join(
            os.getcwd(), self.model_dir, self.model_name_v2))
        self._load_model_v1(os.path.join(
            os.getcwd(), self.model_dir, self.model_name_v1))

    def _load_model_v2(self, model_path):
        session_options = ort.SessionOptions()
        self.inference_session_v2 = ort.InferenceSession(
            model_path, sess_options=session_options, providers=self.providers)
        self.outputs_name_v2 = [
            e.name for e in self.inference_session_v2.get_outputs()]
        self.inference_session_v2.run(self.outputs_name_v2, {self.inference_session_v2.get_inputs()[0].name: [
            np.zeros((3, self.input_size[0], self.input_size[1]), np.float32)
        ]})

    def _load_model_v1(self, model_path):
        session_options = ort.SessionOptions()
        self.inference_session_v1 = ort.InferenceSession(
            model_path, sess_options=session_options, providers=self.providers)
        self.outputs_name_v1 = [
            e.name for e in self.inference_session_v1.get_outputs()]
        self.inference_session_v1.run(self.outputs_name_v1, {self.inference_session_v1.get_inputs()[0].name: [
            np.zeros((3, self.input_size[0], self.input_size[1]), np.float32)
        ]})

    def _predict_v2(self, face_image_bgr):
        blob = cv2.dnn.blobFromImages(
            [face_image_bgr], 1.0 / self.input_std, self.input_size, self.input_mean, swapRB=True)
        outputs = self.inference_session_v2.run(self.outputs_name_v2, {
                                                self.inference_session_v2.get_inputs()[0].name: blob})
        return outputs[0]

    def _predict_v1(self, face_image_bgr):
        blob = cv2.dnn.blobFromImages(
            [face_image_bgr], 1.0 / self.input_std, self.input_size, self.input_mean, swapRB=True)
        outputs = self.inference_session_v1.run(self.outputs_name_v1, {
                                                self.inference_session_v1.get_inputs()[0].name: blob})
        return outputs[0]

    def liveness_detector(self, face_image):
        output_v1 = self._predict_v1(face_image_bgr=face_image)
        output_v2 = self._predict_v2(face_image_bgr=face_image)
        # output_average = ((output_v1 + output_v2) / 2.0)

        prediction_v1 = softmax(output_v1)
        prediction_v2 = softmax(output_v2)
        # label: face is true or fake
        label_v1 = np.argmax(prediction_v1)
        label_v2 = np.argmax(prediction_v2)
        if label_v1 == 1 or label_v2 == 1:
            return True
        else:
            return False
