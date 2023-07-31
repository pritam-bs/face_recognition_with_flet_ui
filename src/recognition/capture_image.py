import cv2


class CaptureImage:
    max_width = 448

    def __init__(self, rtspUrl):
        self._init_camera(rtspUrl)

    def _init_camera(self, rtspUrl):
        self.rtsp_url = rtspUrl
        if rtspUrl is not None:
            self.video_capture = cv2.VideoCapture(self.rtsp_url)
        else:
            self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FPS, 30)
        self.video_capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.video_capture.set(cv2.CAP_PROP_HW_ACCELERATION, 1)

    def __del__(self):
        self.video_capture.release()

    def _capture(self):
        if self.video_capture == None:
            self._init_camera(self.rtsp_url)
        if not self.video_capture.isOpened():
            self.video_capture.release()
            self.video_capture = None
            return None
        try:
            ret, frame = self.video_capture.read()
            frame = cv2.flip(frame, 1)
        except Exception as e:
            print(f"Image capture failed. Error: {e}")
            return None
        if not ret:
            self.video_capture.release()
            self.video_capture = None
            return None
        frame = self._resize_largest_with_aspect_ratio(
            frame, max_width=self.max_width)
        return frame

    def _resize_largest_with_aspect_ratio(self, image, max_width=None, max_height=None):
        # Get the original dimensions of the image
        height, width = image.shape[:2]

        # Calculate the aspect ratio of the image
        aspect_ratio = width / float(height)

        if max_width is not None and max_height is not None:
            # Both max width and max height are provided, calculate the dimensions
            if max_width >= width and max_height >= height:
                # Image is smaller than or equal to both max_width and max_height
                return image

            if max_width / aspect_ratio <= max_height:
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)

        elif max_width is not None:
            # Only max width is provided, check if image width is smaller than max_width
            if max_width >= width:
                # Image width is smaller than or equal to max_width
                return image

            # Calculate new height based on aspect ratio
            new_width = max_width
            new_height = int(new_width / aspect_ratio)

        elif max_height is not None:
            # Only max height is provided, check if image height is smaller than max_height
            if max_height >= height:
                # Image height is smaller than or equal to max_height
                return image

            # Calculate new width based on aspect ratio
            new_height = max_height
            new_width = int(new_height * aspect_ratio)

        else:
            # Both max width and max height are None, return the original image
            return image

        # Resize the image with the calculated dimensions
        image = cv2.resize(image, (new_width, new_height))

        return image

    def getFrame(self):
        frame = self._capture()
        return frame
