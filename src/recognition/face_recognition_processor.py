
from capture_image import CaptureImage
from fas.fas_processor import FasProcessor
from knn_search_processor import KnnSearchProcessor
from person import Person
import queue
import threading
import cv2
import numpy as np
from tqdm import tqdm
from face_detector.cascade_face_detector import CascadeDetector
from feature_generator.arc_face_feature_generator import ArcFaceGenerator


class FaceRecognitionProcessor:
    capture_image = CaptureImage(rtspUrl=None)
    fasProcessor = FasProcessor()
    knnSearchProcessor = KnnSearchProcessor()
    image_queue = queue.Queue(maxsize=1)
    name_queue = queue.Queue(maxsize=1)
    isStopped = False

    def __init__(self):
        self.image_producer_thread = threading.Thread(
            target=self._image_producer_worker)
        self.cascade_detector = CascadeDetector(image_size=(112, 112))
        self.arc_face_generator = ArcFaceGenerator()

    def _face_extractor(self, frame):
        face_image = None
        bbox = None
        if frame is not None:
            for index, frame in tqdm(enumerate([frame]), total=len([frame]), desc="Face Extractor"):
                face_image, bbox = self.cascade_detector.extract_face(
                    image_array=frame)

        return face_image, bbox

    def _face_embedding_creator(self, face_image_list):
        if face_image_list is not None:
            embeddings = self.arc_face_generator.get_feature_vectors(
                face_image_list)
        return embeddings

    def _image_producer_worker(self):
        while True:
            if self.isStopped:
                break
            frame = self.capture_image.getFrame()
            if frame is None:
                continue
            face_image, bbox = self._face_extractor(frame)
            try:
                self.image_queue.put((frame, bbox))
            except Exception as e:
                pass
            if face_image is None and bbox is None:
                continue
            embeddings = self._face_embedding_creator([face_image])
            if embeddings is None:
                continue
            matched_person_name = self.knnSearchProcessor.search(embeddings)
            try:
                self.name_queue.put(matched_person_name)
            except Exception as e:
                pass
            print(f"Match Person Name: {matched_person_name}")


def main():
    faceRecognitionProcessor = FaceRecognitionProcessor()
    faceRecognitionProcessor.image_producer_thread.start()

    while True:
        frame = None
        name = None
        try:
            (frame, bbox) = faceRecognitionProcessor.image_queue.get(block=False)
            faceRecognitionProcessor.image_queue.task_done()
            name = faceRecognitionProcessor.name_queue.get(block=False)
        except Exception as e:
            pass
        if frame is not None:
            if name is None:
                name = "Unknown"
            if bbox is not None:
                color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)
                x, y, w, h = bbox
                left = x
                up = y
                right = x + w
                down = y + h
                cv2.line(frame, (left, up), (right, up), color, 3, cv2.LINE_AA)
                cv2.line(frame, (right, up), (right, down),
                         color, 3, cv2.LINE_AA)
                cv2.line(frame, (right, down), (left, down),
                         color, 3, cv2.LINE_AA)
                cv2.line(frame, (left, down), (left, up),
                         color, 3, cv2.LINE_AA)

                xx, yy = np.max([bbox[0] - 10, 10]), np.max([bbox[1] - 10, 10])
                cv2.putText(frame, "Name: {}".format(
                    name), (xx, yy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Display the image
            cv2.imshow('Face Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                faceRecognitionProcessor.isStopped = True
                break

    faceRecognitionProcessor.image_producer_thread.join()
    print("Ending image producer thread")


if __name__ == "__main__":
    main()
