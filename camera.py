import cv2
from datetime import datetime

class Camera:
    def __init__(self, source=0, frame_rate=15):
        self.cap = cv2.VideoCapture(source)
        self.frame_rate = frame_rate

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cv2.putText(frame, timestamp, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame, timestamp

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
