import numpy as np
import os
import onnxruntime as ort
import cv2
from scipy.special import softmax


class FasProcessor:
    model_dir = 'src/models/fas_detection'
    model_name_v2 = "2.7_80x80_MiniFASNetV2.onnx"
    model_name_v1 = "4_0_0_80x80_MiniFASNetV1SE.onnx"
    h_input = 80
    w_input = 80

    ort.set_default_logger_severity(0)
    providers = [
        "CPUExecutionProvider",
        ('CUDAExecutionProvider', {
            'device_id': 0,
            'arena_extend_strategy': 'kNextPowerOfTwo',
            'gpu_mem_limit': 1 * 1024 * 1024 * 1024,
            'cudnn_conv_algo_search': 'EXHAUSTIVE',
            'do_copy_in_default_stream': True
        })
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
            np.zeros((3, self.h_input, self.w_input), np.float32)
        ]})

    def _load_model_v1(self, model_path):
        session_options = ort.SessionOptions()
        self.inference_session_v1 = ort.InferenceSession(
            model_path, sess_options=session_options, providers=self.providers)
        self.outputs_name_v1 = [
            e.name for e in self.inference_session_v1.get_outputs()]
        self.inference_session_v1.run(self.outputs_name_v1, {self.inference_session_v1.get_inputs()[0].name: [
            np.zeros((3, self.h_input, self.w_input), np.float32)
        ]})

    def _predict_v2(self, imm_RGB):
        resize_img = cv2.resize(imm_RGB, (self.w_input, self.h_input))
        resize_image_channel_first = np.transpose(resize_img, (2, 0, 1))
        face_imgs = (np.array([resize_image_channel_first])).astype(np.float32)
        batch_size = len(face_imgs)
        sample_shape = face_imgs[0].shape
        sample_dtype = face_imgs[0].dtype
        batch_array = np.empty(
            (batch_size,) + sample_shape, dtype=sample_dtype)
        for i, sample in enumerate(face_imgs):
            batch_array[i] = sample

        outputs = self.inference_session_v2.run(self.outputs_name_v2, {
                                                self.inference_session_v2.get_inputs()[0].name: batch_array})
        return outputs[0]

    def _predict_v1(self, imm_RGB):
        resize_img = cv2.resize(imm_RGB, (self.w_input, self.h_input))
        resize_image_channel_first = np.transpose(resize_img, (2, 0, 1))
        face_imgs = (np.array([resize_image_channel_first])).astype(np.float32)
        batch_size = len(face_imgs)
        sample_shape = face_imgs[0].shape
        sample_dtype = face_imgs[0].dtype
        batch_array = np.empty(
            (batch_size,) + sample_shape, dtype=sample_dtype)
        for i, sample in enumerate(face_imgs):
            batch_array[i] = sample

        outputs = self.inference_session_v1.run(self.outputs_name_v1, {
                                                self.inference_session_v1.get_inputs()[0].name: batch_array})
        return outputs[0]

    def liveness_detector(self, face_image, image_format="BGR"):
        imm_RGB = face_image[:, :, ::-
                             1] if image_format == "BGR" else face_image

        output_v1 = self._predict_v1(imm_RGB=imm_RGB)
        output_v2 = self._predict_v2(imm_RGB=imm_RGB)
        output_average = ((output_v1 + output_v2) / 2.0)

        prediction = softmax(output_average)
        # label: face is true or fake
        label = np.argmax(prediction)
        if label == 1:
            return True
        else:
            return False
