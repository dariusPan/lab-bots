from config import VIDEO_SOURCE, FRAME_RATE, LOG_FILE
from camera import Camera
from logger import Logger
from roi_manager import ROIManager
from gui import ExperimentGUI

def main():
    cam = Camera(VIDEO_SOURCE, FRAME_RATE)
    logger = Logger(LOG_FILE)
    roi_manager = ROIManager()

    # # Example ROI
    # roi_manager.add_box((100, 100), (300, 300))
    # print("Initialized ROI at (100,100) to (300,300)")

    gui = ExperimentGUI(cam, logger, roi_manager)
    gui.start()

if __name__ == "__main__":
    main()
