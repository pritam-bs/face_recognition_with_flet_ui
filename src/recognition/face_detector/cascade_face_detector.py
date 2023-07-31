import os
import cv2


class CascadeDetector:
    default_cascade_model_path = os.path.join(
        os.getcwd(), "src/models/haarcascade/haarcascade_frontalface_default.xml")

    def __init__(self, cascade_model_path=default_cascade_model_path, image_size=(112, 112)) -> None:
        self.image_size = image_size
        self.cascade_model_path = cascade_model_path
        # Load the Haar Cascade face detection model
        self.face_cascade = cv2.CascadeClassifier(self.cascade_model_path)

    def extract_face(self, frame):
        try:
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the image
            faces = self.face_cascade.detectMultiScale(
                gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(112, 112))

            # Find the largest face
            largest_face = None
            largest_area = 0
            for (x, y, w, h) in faces:
                area = w * h
                if area > largest_area:
                    largest_area = area
                    largest_face = (x, y, w, h)

            # Extract the largest face and resize it
            if largest_face is not None:
                (x, y, w, h) = largest_face
                face_image = frame[y:y+h, x:x+w]
                face_image = cv2.resize(face_image, self.image_size)
                return face_image, largest_face
            else:
                return None, None
        except Exception as e:
            return None, None
