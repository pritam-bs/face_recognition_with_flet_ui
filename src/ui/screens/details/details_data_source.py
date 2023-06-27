from fletched.mvp import MvpDataSource
from fletched.mvp import MvpModel
from typing import Optional, List
from ui.app import App
from recognition.capture_image import CaptureImage
from tqdm import tqdm
from recognition.face_detector.cascade_face_detector import CascadeDetector
from recognition.fas.fas_processor import FasProcessor
import rx
import cv2
import base64
from data_models.employee import Employee
from api.api_client import APIClient
from settings import settings
from rx.subject.asyncsubject import AsyncSubject
from logger import logger
from app_errors.app_error import ErrorModel
from storage.client_storage import ClientStorage


class DetailsModel(MvpModel):
    is_loading: Optional[bool] = None
    frame_image_base64: Optional[str] = None
    employee_list: Optional[List[Employee]] = None
    matched_employee: Optional[Employee] = None
    app_error: Optional[ErrorModel] = None


class DetailsDataSource(MvpDataSource):
    current_model = DetailsModel()

    def __init__(self, *, app: App | None, route_params: dict[str, str]) -> None:
        super().__init__(app=app, route_params=route_params)
        self.opm_api_client = APIClient.create(settings.opm_base_url)
        self.capture_image = CaptureImage(rtspUrl=None)
        self.cascade_detector = CascadeDetector(image_size=(112, 112))
        self.fasProcessor = FasProcessor()
        self._strat_image_producer()

    def _strat_image_producer(self):
        self.observable = rx.interval(1.0/30.0)
        self.subscription = self.observable.subscribe(
            on_next=self._image_producer_worker)

    def _image_producer_worker(self, interval):
        frame = self.capture_image.getFrame()
        if frame is None:
            return

        face_image, bbox = self._face_extractor(frame=frame)
        if face_image is not None and bbox is not None:
            color = (0, 0, 255)
            if self.fasProcessor.liveness_detector(frame=frame, bbox=bbox, image_format="BGR"):
                color = (0, 255, 0)
            x, y, w, h = bbox
            left = x
            up = y
            right = x + w
            down = y + h
            cv2.line(frame, (left, up), (right, up), color, 1, cv2.LINE_AA)
            cv2.line(frame, (right, up), (right, down),
                     color, 1, cv2.LINE_AA)
            cv2.line(frame, (right, down), (left, down),
                     color, 1, cv2.LINE_AA)
            cv2.line(frame, (left, down), (left, up),
                     color, 1, cv2.LINE_AA)

        retval, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        self.update_model_complete(
            new_model={"frame_image_base64": jpg_as_text})

    def _face_extractor(self, frame):
        face_image = None
        bbox = None
        if frame is not None:
            # for index, frame in tqdm(enumerate([frame]), total=len([frame]), desc="Face Extractor"):
            for index, frame in enumerate([frame]):
                face_image, bbox = self.cascade_detector.extract_face(
                    image_array=frame)

        return face_image, bbox

    def get_employees_info(self):
        self.update_model_complete(new_model={"is_loading": True})

        self.opm_api_client.get().set_path("employees")

        # Make the API call and get the observable
        observable: AsyncSubject = self.opm_api_client.make_request(
            model_type=List[Employee])

        # Subscribe to the observable to receive the API response
        def on_next(data):
            logger.debug(data)
            self._save_employees_info_to_storage(employees=data)
            self.update_model_complete(new_model={
                "is_loading": False,
                "employee_list": data
            })

        def on_error(error):
            logger.debug(error)
            self.update_model_complete(new_model={
                "is_loading": False,
                "app_error": error,
                "employee_list": []
            })

        observable.subscribe(on_next=on_next, on_error=on_error).dispose()

    def _save_employees_info_to_storage(self, employees: List[Employee]):
        client_storage = ClientStorage(page=self.app.page)
        client_storage.save_employee_list(employee_list=employees)

    def _get_employee_dict_from_storage(self):
        client_storage = ClientStorage(page=self.app.page)
        employee_dict = client_storage.get_employee_dict()
        return employee_dict

    def _get_employee_details(self, employee_id):
        client_storage = ClientStorage(page=self.app.page)
        employee_dict = client_storage.get_employee_dict()
        employee_info = employee_dict[employee_id]
        return employee_info

    def _show_matched_employee_details(self, employee_id):
        employee_info = self._get_employee_details(employee_id=employee_id)
        self.update_model_complete(
            new_model={"matched_employee": employee_info})
