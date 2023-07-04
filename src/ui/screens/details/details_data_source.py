from fletched.mvp import MvpDataSource
from fletched.mvp import MvpModel
from typing import Optional, List, Union, Dict
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
from rx.subject import Subject
from rx.operators import distinct_until_changed
from logger import logger
from app_errors.app_error import ErrorModel
from storage.client_storage import ClientStorage
from recognition.feature_generator.arc_face_feature_generator import ArcFaceGenerator
from recognition.knn_search_processor import KnnSearchProcessor
from data_models.employee import Meal


class DetailsModel(MvpModel):
    is_loading: Optional[bool] = None
    frame_image_base64: Optional[str] = None
    employee_list: Optional[List[Employee]] = None
    meal_found: Optional[Employee] = None
    no_meal_found: Optional[str] = None
    app_error: Optional[ErrorModel] = None
    is_meal_consumption_successful: Optional[bool] = None


class DetailsDataSource(MvpDataSource):
    current_model = DetailsModel()

    def __init__(self, *, app: Union[App, None], route_params: Dict[str, str]) -> None:
        super().__init__(app=app, route_params=route_params)
        self.opm_api_client = APIClient.create(settings.opm_base_url)
        self.capture_image = CaptureImage(rtspUrl=None)
        self.cascade_detector = CascadeDetector(image_size=(112, 112))
        self.fasProcessor = FasProcessor()
        self.arc_face_generator = ArcFaceGenerator()
        self.knnSearchProcessor = KnnSearchProcessor()
        self.matched_subject = Subject()
        self.matched_subscription = self.matched_subject.pipe(
            distinct_until_changed()
        ) .subscribe(on_next=self._on_matched)
        self._strat_image_producer()

    def __del__(self):
        self.matched_subscription.dispose()
        self.image_producer_subscription.dispose()

    def _strat_image_producer(self):
        self.observable = rx.interval(1.0/30.0)
        self.image_producer_subscription = self.observable.subscribe(
            on_next=self._image_producer_worker)

    def _image_producer_worker(self, interval):
        frame = self.capture_image.getFrame()
        if frame is None:
            return

        face_image, bbox = self._face_extractor(frame=frame)
        is_live = None
        if bbox is not None:
            is_live = True
            # is_live = self.fasProcessor.liveness_detector(
            #     frame=frame, bbox=bbox, image_format="BGR")

        self._update_image_for_viewing(
            frame=frame, bbox=bbox, is_live=is_live)

        if face_image is not None and bbox is not None and is_live:
            embeddings = self._face_embedding_creator(
                face_image_list=[face_image])
            matched_id = self._search(embeddings=embeddings)
            if matched_id is not None:
                self.matched_subject.on_next(matched_id)

    def _face_extractor(self, frame):
        face_image = None
        bbox = None
        if frame is not None:
            # for index, frame in tqdm(enumerate([frame]), total=len([frame]), desc="Face Extractor"):
            for index, frame in enumerate([frame]):
                face_image, bbox = self.cascade_detector.extract_face(
                    image_array=frame)

        return face_image, bbox

    def _face_embedding_creator(self, face_image_list):
        if face_image_list is not None:
            embeddings = self.arc_face_generator.get_feature_vectors(
                face_image_list)
        return embeddings

    def _search(self, embeddings):
        matched_id = self.knnSearchProcessor.search(
            embeddings=embeddings)
        return matched_id

    def _on_matched(self, matched_id):
        logger.debug(f"Matched ID: {matched_id}")
        self._show_matched_employee_details(employee_id=matched_id)

    def _update_image_for_viewing(self, frame, bbox, is_live):
        if bbox is not None:
            color = (0, 0, 255)
            if is_live is not None and is_live:
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

    def submit_meal_consumption(self, employee_id: str, meal: Meal):
        self.update_model_complete(new_model={"is_loading": True})
        self.opm_api_client.post().set_path("meal").set_params(
            {"employee_id": employee_id, "meal": meal.value})

        # Make the API call and get the observable
        observable: AsyncSubject = self.opm_api_client.make_request(
            model_type=List[Employee])

        # Subscribe to the observable to receive the API response
        def on_next(data):
            logger.debug(data)
            self._save_employees_info_to_storage(employees=data)
            self.update_model_complete(new_model={
                "is_loading": False,
                "is_meal_consumption_successful": True,
                "employee_list": data
            })

        def on_error(error):
            logger.debug(error)
            self.update_model_complete(new_model={
                "is_loading": False,
                "is_meal_consumption_successful": False,
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
        if employee_dict is not None and employee_id in employee_dict:
            employee_info = employee_dict[employee_id]
            return employee_info
        return None

    def _show_matched_employee_details(self, employee_id):
        employee_info = self._get_employee_details(employee_id=employee_id)
        if employee_info is None:
            self.update_model_complete(
                new_model={"no_meal_found": employee_id})
        else:
            self.update_model_complete(
                new_model={"meal_found": employee_info})
