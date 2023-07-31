import numpy as np
import os
import onnxruntime as ort
import numpy as np
from logger import logger


class ArcFaceGenerator:
    _instance = None
    model_path = os.path.join(
        os.getcwd(), "src/models/arc_face/model.onnx")

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
    ort.set_default_logger_severity(0)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, model_path=model_path):
        if isinstance(model_path, str) and model_path.endswith(".onnx"):
            session_options = ort.SessionOptions()
            self.inference_session = ort.InferenceSession(
                model_path, sess_options=session_options, providers=self.providers)
            outputs = [e.name for e in self.inference_session.get_outputs()]
            self.inference_session.run(outputs, {self.inference_session.get_inputs()[0].name: [
                np.zeros((112, 112, 3), np.float32)
            ]})
        else:
            self.inference_session = model_path

    def get_feature_vectors(self, face_img):
        # preprocess input
        face_img = ((np.array(face_img) - 127.5)
                    * 0.0078125).astype(np.float32)
        outputs = [e.name for e in self.inference_session.get_outputs()]
        embeddings = self.inference_session.run(
            outputs, {self.inference_session.get_inputs()[0].name: face_img})

        return embeddings[0].flatten()
