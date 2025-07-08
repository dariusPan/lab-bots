import cv2

class ROIManager:
    def __init__(self):
        self.roi_boxes = []

    def add_box(self, top_left, bottom_right):
        self.roi_boxes.append((top_left, bottom_right))

    def clear_boxes(self):
        self.roi_boxes = []

    def draw_rois(self, frame, color=(0, 255, 0)):
        for box in self.roi_boxes:
            cv2.rectangle(frame, box[0], box[1], color, 2)
