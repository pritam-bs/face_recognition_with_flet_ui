import threading
import queue
from person import Person
from tqdm import tqdm
from face_detector.yolo_v5_face_detector import YoloV5FaceDetector


class FaceExtractorProcessor:
    face_extractor_thread = None
    is_stop = False

    def __init__(self):
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.yolo_detector = YoloV5FaceDetector(image_size=(112, 112))

    def _add_task(self, person: Person):
        self.input_queue.put(person)

    def get_result(self):
        result = self.output_queue.get()
        return result

    def add_person(self, person: Person):
        if self.face_extractor_thread is None:
            self.face_extractor_thread = threading.Thread(
                target=self._face_extractor_worker, args=(self.input_queue, self.output_queue,))
            self.face_extractor_thread.start()
        return self._add_task(person=person)

    def _face_extractor_worker(self, input_queue, output_queue):
        while True:
            person: Person = input_queue.get()
            input_queue.task_done()
            if person is None:
                output_queue.put(None)
                break
            face_image_list = []
            bbs_list = []
            for index, frame_array in tqdm(enumerate(person.frame_list), total=len(person.face_image_list), desc="Face Extractor {}".format(person.name)):
                bbs, pps, ccs, nimgs = self.yolo_detector.detect_in_image(
                    image=frame_array, image_format="BGR")
                if len(nimgs) > 0 and nimgs[0] is not None and len(bbs) > 0 and bbs[0] is not None:
                    face_image_list.append(nimgs[0])
                    bbs_list.append(bbs[0])

            person.face_image_list = face_image_list
            person.bbs_list = bbs_list
            output_queue.put(person)

    def stop(self):
        while not self.input_queue.empty():
            self.input_queue.get()
            self.input_queue.task_done()
        self.input_queue.join()
        while not self.output_queue.empty():
            self.output_queue.get()
            self.output_queue.task_done()
        self.output_queue.join()
        if self.face_extractor_thread is not None:
            self.face_extractor_thread.join()
