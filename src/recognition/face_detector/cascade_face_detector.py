import os
import cv2
from PIL import Image
from numpy import asarray


class CascadeDetector:
    default_cascade_model_path = os.path.join(
        os.getcwd(), "src/models/haarcascade/haarcascade_frontalface_default.xml")

    def __init__(self, cascade_model_path=default_cascade_model_path, image_size=(112, 112)) -> None:
        self.image_size = image_size
        self.cascade_model_path = cascade_model_path
        # Load the Haar Cascade face detection model
        self.face_cascade = cv2.CascadeClassifier(self.cascade_model_path)

    def extract_face(self, image_array):
        try:
            # Convert the image to grayscale
            image = Image.fromarray(image_array)
            gray_image = image.convert('L')
            gray_image_array = asarray(gray_image)

            # Detect faces in the image
            faces = self.face_cascade.detectMultiScale(
                gray_image_array, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

            # Find the largest face
            largest_face = None
            largest_area = 0
            for (x, y, w, h) in faces:
                area = w * h
                if area > largest_area:
                    largest_area = area
                    largest_face = (x, y, w, h)

            # Extract the largest face and resize it to (160, 160)
            if largest_face is not None:
                (x, y, w, h) = largest_face
                face_array = image_array[y:y+h, x:x+w]
                image = Image.fromarray(face_array)
                image = image.resize(self.image_size)
                face_array = asarray(image)
                return face_array, largest_face
            else:
                return None, None
        except Exception as e:
            return None, None
