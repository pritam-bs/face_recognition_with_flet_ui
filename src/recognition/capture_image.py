import cv2


class CaptureImage:
    min_size = 300

    def __init__(self, rtspUrl):
        self._init_camera(rtspUrl)

    def _init_camera(self, rtspUrl):
        if rtspUrl is not None:
            self.rtsp_url = rtspUrl
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
        except Exception as e:
            print(f"Image capture failed. Error: {e}")
            return None
        if not ret:
            self.video_capture.release()
            self.video_capture = None
            return None

        # Resize the image while keeping the aspect ratio fixed
        if self.min_size is not None:
            h, w = frame.shape[:2]
            if min(h, w) < self.min_size:
                if h < w:
                    new_h = self.min_size
                    new_w = int(new_h * (w / h))
                else:
                    new_w = self.min_size
                    new_h = int(new_w * (h / w))
                resized_frame = cv2.resize(
                    frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            else:
                aspect_ratio = w / h
                new_h = self.min_size
                new_w = int(new_h * aspect_ratio)
                if new_w > self.min_size:
                    new_w = self.min_size
                    new_h = int(new_w / aspect_ratio)
                resized_frame = cv2.resize(
                    frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

            return resized_frame
        else:
            return frame

    def getFrame(self):
        frame = self._capture()
        return frame
