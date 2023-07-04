from keras.models import load_model
import numpy as np
import os
import tensorflow as tf
from sklearn.preprocessing import normalize
from absl import logging
from logger import logger

# gpus = tf.config.experimental.list_physical_devices("GPU")
# for gpu in gpus:
#     tf.config.experimental.set_memory_growth(gpu, True)

gpus = tf.config.list_physical_devices('GPU')
gpu_id = 0
if gpus:
    # Restrict TensorFlow to only use only one GPU based on gpu_id
    try:
        tf.config.set_visible_devices(gpus[gpu_id], 'GPU')
        logical_gpus = tf.config.list_logical_devices('GPU')
        logger.debug(len(gpus), "Physical GPUs,",
                     len(logical_gpus), "Logical GPU")
    except RuntimeError as e:
        # Visible devices must be set before GPUs have been initialized
        logger.debug(e)


class ArcFaceGenerator:
    _instance = None
    logger = tf.get_logger()
    logger.disabled = True
    logger.setLevel(logging.FATAL)

    default_detector = os.path.join(
        os.getcwd(), "src/models/arc_face/glint360k_cosface_r100_fp16_0.1.h5")

    file_hash = {"glint360k_cosface": "e39a16ace2ba11edb5ea0242ac120002"}
    default_model_http = "http://github.com/leondgarse/Keras_insightface/releases/download/v1.0.0/glint360k_cosface_r100_fp16_0.1.h5"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, model_path=default_detector):
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

        # Add a pooling layer and a dense layer for merging the embeddings
        # Add some convolutional layers
        # x = self.model.output
        # x = Reshape((1, 1, self.model.output_shape[-1]))(x)
        # x = GlobalAveragePooling2D()(x)
        # x = Dense(self.model.output_shape[-1], activation='relu')(
        #     x)

    def get_feature_vectors(self, image_list):
        # preprocess input
        image_list = (np.array(image_list) - 127.5) * 0.0078125

        batch_size = len(image_list)
        sample_shape = image_list[0].shape
        sample_dtype = image_list[0].dtype

        # create an empty batch with the correct shape and dtype
        batch_array = np.empty(
            (batch_size,) + sample_shape, dtype=sample_dtype)

        # copy the image arrays into the batch
        for i, sample in enumerate(image_list):
            batch_array[i] = sample
        embeddings = self.model.predict(
            batch_array, batch_size=batch_size)

        return embeddings
