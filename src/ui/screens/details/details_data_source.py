from fletched.mvp import MvpDataSource
from fletched.mvp import MvpModel, ErrorMessage
from typing import Optional
from ui.app import App
from recognition.capture_image import CaptureImage
from tqdm import tqdm
from recognition.face_detector.cascade_face_detector import CascadeDetector
import rx
import cv2
import base64


class DetailsModel(MvpModel):
    is_loading: Optional[bool] = False
    frame_image_base64: Optional[str] = None


class DetailsDataSource(MvpDataSource):
    current_model = DetailsModel()

    def __init__(self, *, app: App | None, route_params: dict[str, str]) -> None:
        super().__init__(app=app, route_params=route_params)
        self.capture_image = CaptureImage(rtspUrl=None)
        self.cascade_detector = CascadeDetector(image_size=(112, 112))
        self._strat_image_producer()

    def _strat_image_producer(self):
        self.observable = rx.interval(1.0/30.0)
        self.subscription = self.observable.subscribe(
            on_next=self._image_producer_worker)

    def _image_producer_worker(self, interval):
        frame = self.capture_image.getFrame()
        if frame is None:
            return
        retval, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        self.update_model_partial(
            changes={"frame_image_base64": jpg_as_text})

    def _face_extractor(self, frame):
        face_image = None
        bbox = None
        if frame is not None:
            for index, frame in tqdm(enumerate([frame]), total=len([frame]), desc="Face Extractor"):
                face_image, bbox = self.cascade_detector.extract_face(
                    image_array=frame)

        return face_image, bbox
