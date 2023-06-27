import numpy as np
import os
import torch
from recognition.fas.MiniFASNet import MiniFASNetV1, MiniFASNetV2, MiniFASNetV1SE, MiniFASNetV2SE
from recognition.fas.fas_utility import parse_model_name, get_kernel
from recognition.fas import transform as trans
import torch.nn.functional as F
from recognition.fas.crop_image import CropImage
from logger import logger


class FasProcessor:
    modelMapping = {
        'MiniFASNetV1': MiniFASNetV1,
        'MiniFASNetV2': MiniFASNetV2,
        'MiniFASNetV1SE': MiniFASNetV1SE,
        'MiniFASNetV2SE': MiniFASNetV2SE
    }
    model_dir = 'src/models/fas_detection'
    model_name_v2 = "2.7_80x80_MiniFASNetV2.pth"
    model_name_v1 = "4_0_0_80x80_MiniFASNetV1SE.pth"
    model_v2 = None
    model_v1 = None
    scoreThreshold = 0.99

    def __init__(self):
        self.device = torch.device("cuda:{}".format(0)
                                   if torch.cuda.is_available() else "cpu")
        self._load_model_v2(os.path.join(
            os.getcwd(), self.model_dir, self.model_name_v2))
        self.model_v2.eval()
        self._load_model_v1(os.path.join(
            os.getcwd(), self.model_dir, self.model_name_v1))
        self.model_v1.eval()

    def _load_model_v2(self, modelPath):
        # define model
        model_name = os.path.basename(modelPath)
        h_input, w_input, model_type, _ = parse_model_name(model_name)
        self.kernel_size = get_kernel(h_input, w_input,)
        self.model_v2 = self.modelMapping[model_type](
            conv6_kernel=self.kernel_size).to(self.device)

        # load model weight
        state_dict = torch.load(modelPath, map_location=self.device)
        keys = iter(state_dict)
        first_layer_name = keys.__next__()
        if first_layer_name.find('module.') >= 0:
            from collections import OrderedDict
            new_state_dict = OrderedDict()
            for key, value in state_dict.items():
                name_key = key[7:]
                new_state_dict[name_key] = value
            self.model_v2.load_state_dict(new_state_dict)
        else:
            self.model_v2.load_state_dict(state_dict)
        return None

    def _load_model_v1(self, modelPath):
        # define model
        model_name = os.path.basename(modelPath)
        h_input, w_input, model_type, _ = parse_model_name(model_name)
        self.kernel_size = get_kernel(h_input, w_input,)
        self.model_v1 = self.modelMapping[model_type](
            conv6_kernel=self.kernel_size).to(self.device)

        # load model weight
        state_dict = torch.load(modelPath, map_location=self.device)
        keys = iter(state_dict)
        first_layer_name = keys.__next__()
        if first_layer_name.find('module.') >= 0:
            from collections import OrderedDict
            new_state_dict = OrderedDict()
            for key, value in state_dict.items():
                name_key = key[7:]
                new_state_dict[name_key] = value
            self.model_v1.load_state_dict(new_state_dict)
        else:
            self.model_v1.load_state_dict(state_dict)
        return None

    def _predict_v2(self, imm_RGB, bbox):
        h_input, w_input, model_type, scale = parse_model_name(
            self.model_name_v2)

        image_cropper = CropImage()
        crop_param = {
            "org_img": imm_RGB,
            "bbox": bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True,
        }
        if scale is None:
            crop_param["crop"] = False
        cropped_image = image_cropper.crop(**crop_param)

        test_transform = trans.Compose([
            trans.ToTensor(),
        ])
        frame = test_transform(cropped_image)
        frame = frame.unsqueeze(0).to(self.device)
        with torch.no_grad():
            result = self.model_v2.forward(frame)
            result = F.softmax(result).cpu().numpy()
        return result

    def _predict_v1(self, imm_RGB, bbox):
        h_input, w_input, model_type, scale = parse_model_name(
            self.model_name_v1)

        image_cropper = CropImage()
        crop_param = {
            "org_img": imm_RGB,
            "bbox": bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True,
        }
        if scale is None:
            crop_param["crop"] = False
        cropped_image = image_cropper.crop(**crop_param)

        test_transform = trans.Compose([
            trans.ToTensor(),
        ])
        frame = test_transform(cropped_image)
        frame = frame.unsqueeze(0).to(self.device)
        with torch.no_grad():
            result = self.model_v1.forward(frame)
            result = F.softmax(result).cpu().numpy()
        return result

    def liveness_detector(self, frame, bbox, image_format="BGR"):
        imm_RGB = frame[:, :, ::-1] if image_format == "BGR" else frame
        prediction = np.zeros((1, 3))
        # sum the prediction from single model's result
        # get perdiction using model_v2

        prediction += self._predict_v1(imm_RGB=imm_RGB, bbox=bbox)
        prediction += self._predict_v2(imm_RGB=imm_RGB, bbox=bbox)
        # label: face is true or fake
        label = np.argmax(prediction)
        # value: the score of prediction
        value = prediction[0][label]/2
        if label == 1 and value > self.scoreThreshold:
            # logger.debug("RealFace Score: {:.2f}".format(value))
            return True
        else:
            # logger.debug("FakeFace Score: {:.2f}".format(value))
            return False
