import cv2
import os
import numpy as np

class ImageRecognitionUtils:
    def __init__(self):
        self.yolo_net = None
        self.yolo_classes = []

        # Paths to model files
        cfg_path = "models/yolov4-tiny.cfg"
        weights_path = "models/yolov4-tiny.weights"
        labels_path = "models/coco.names"
        os.makedirs("models", exist_ok=True)

        # Load YOLO network
        if os.path.exists(cfg_path) and os.path.exists(weights_path):
            try:
                self.yolo_net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)
                self.yolo_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.yolo_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                print("[Objects] YOLOv4-Tiny loaded successfully from .cfg and .weights")
            except Exception as e:
                print("[Objects] Failed to load YOLOv4-Tiny:", e)
        else:
            print("[Objects] YOLOv4-Tiny .cfg or .weights file missing in models/")

        # Load class labels
        if os.path.exists(labels_path):
            try:
                with open(labels_path, "r") as f:
                    self.yolo_classes = [line.strip() for line in f.readlines()]
                print("[Objects] COCO classes loaded.")
            except Exception as e:
                print("[Objects] Failed to load COCO classes:", e)
        else:
            print("[Objects] coco.names file missing in models/")

    def detect_objects(self, roi, conf_threshold=0.5):
        """
        Detect objects in ROI using YOLOv4 Tiny and return bounding boxes.
        """
        if self.yolo_net is None:
            print("⚠️ YOLO model not loaded, skipping detection.")
            return []
        if roi.shape[0] < 32 or roi.shape[1] < 32:
            print("⚠️ ROI too small for object detection, skipping.")
            return []

        try:
            blob = cv2.dnn.blobFromImage(roi, scalefactor=1/255.0, size=(416, 416),
                                        swapRB=True, crop=False)
            self.yolo_net.setInput(blob)
            layer_names = self.yolo_net.getLayerNames()
            output_layers = [layer_names[i - 1] for i in self.yolo_net.getUnconnectedOutLayers()]
            outputs = self.yolo_net.forward(output_layers)
        except Exception as e:
            print(f"⚠️ Error running YOLO detection: {e}")
            return []

        height, width = roi.shape[:2]
        boxes = []
        class_ids = []
        confidences = []

        # Parse YOLO outputs
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = int(np.argmax(scores))
                confidence = scores[class_id]
                if confidence > conf_threshold:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    class_ids.append(class_id)
                    confidences.append(float(confidence))

        # Apply Non-Maximum Suppression (to remove duplicates)
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, 0.4)

        results = []
        if len(indices) > 0:
            # Fix for OpenCV version differences
            if isinstance(indices, (tuple, list)):
                indices = [i[0] if isinstance(i, (list, np.ndarray)) else i for i in indices]

            for i in indices:
                label = self.yolo_classes[class_ids[i]] if self.yolo_classes else str(class_ids[i])
                results.append({
                    "box": boxes[i],
                    "label": label,
                    "confidence": confidences[i]
                })
        return results

    
    def detect_color_change(self, roi, target_bgr, threshold=30):
        """
        Compare the mean color of the ROI to the target color.
        Returns True if the color difference exceeds the threshold.
        """
        import numpy as np  # make sure numpy is imported at top
        # Compute mean color of the ROI
        mean_color = cv2.mean(roi)[:3]  # Exclude alpha if present
        diff = np.linalg.norm(np.array(mean_color) - np.array(target_bgr))
        return diff > threshold, mean_color

