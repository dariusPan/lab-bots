import tkinter as tk
from PIL import Image, ImageTk
import cv2
from utils import ImageRecognitionUtils

class ExperimentGUI:
    def __init__(self, camera, logger, roi_manager):
        self.camera = camera
        self.logger = logger
        self.roi_manager = roi_manager
        self.vision_utils = ImageRecognitionUtils()
        self.root = tk.Tk()
        self.root.title("Experiment Monitoring Tool")

        # Video display
        self.video_label = tk.Label(self.root)
        self.video_label.pack()
        self.video_label.bind("<Button-1>", self.start_draw_roi)  # Left mouse click
        self.video_label.bind("<B1-Motion>", self.update_draw_roi)
        self.video_label.bind("<ButtonRelease-1>", self.finish_draw_roi)

        # Controls frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        # Take photo button
        self.capture_btn = tk.Button(btn_frame, text="Take Photo", command=self.take_photo)
        self.capture_btn.grid(row=0, column=0, padx=5)

        # Start/Stop recording
        self.record_btn = tk.Button(btn_frame, text="Start Recording", command=self.toggle_recording)
        self.record_btn.grid(row=0, column=1, padx=5)

        # Filename entry for video
        self.filename_entry = tk.Entry(btn_frame, width=20)
        self.filename_entry.insert(0, "output.avi")
        self.filename_entry.grid(row=0, column=2, padx=5)

        # Clear ROI button
        self.clear_roi_btn = tk.Button(btn_frame, text="Clear ROI", command=self.clear_roi)
        self.clear_roi_btn.grid(row=0, column=3, padx=5)

        # Interval photo capture
        interval_frame = tk.Frame(self.root)
        interval_frame.pack(pady=5)
        tk.Label(interval_frame, text="Interval (s):").grid(row=0, column=0)
        self.interval_entry = tk.Entry(interval_frame, width=5)
        self.interval_entry.insert(0, "5")
        self.interval_entry.grid(row=0, column=1, padx=5)
        self.interval_btn = tk.Button(interval_frame, text="Start Interval Capture", command=self.toggle_interval_capture)
        self.interval_btn.grid(row=0, column=2, padx=5)
        
        # Eyedropper for color selection
        self.target_color = None
        self.color_display = tk.Label(btn_frame, text="Selected Color: None", width=30)
        self.color_display.grid(row=1, column=0, padx=5)

        self.eyedrop_btn = tk.Button(btn_frame, text="Select Target Color", command=self.pick_target_color)
        self.eyedrop_btn.grid(row=1, column=1, padx=5)

        # Start/Stop color monitoring
        self.color_monitoring = False
        self.color_btn = tk.Button(btn_frame, text="Start Color Monitoring", command=self.toggle_color_monitoring)
        self.color_btn.grid(row=1, column=2, padx=5)

        # Start/Stop object monitoring
        self.object_monitoring = False
        self.object_btn = tk.Button(btn_frame, text="Start Object Monitoring", command=self.toggle_object_monitoring)
        self.object_btn.grid(row=1, column=3, padx=5)
        
        # Close program button
        self.close_btn = tk.Button(self.root, text="Close Program", command=self.on_close, bg="red", fg="white")
        self.close_btn.pack(pady=10)

        # Flags
        self.running = True
        self.recording = False
        self.video_writer = None
        self.interval_capture = False
        self.color_picking_mode = False

        # ROI drawing state
        self.drawing_roi = False
        self.roi_start = None
        self.temp_frame = None

        # Start video update loop
        self.update_video()

    def take_photo(self):
        frame, timestamp = self.camera.get_frame()
        if frame is not None:
            rois = self.roi_manager.roi_boxes
            if rois:
                # Save each ROI separately
                for idx, (start, end) in enumerate(rois, start=1):
                    x1, y1 = start
                    x2, y2 = end
                    x1, x2 = sorted([x1, x2])
                    y1, y2 = sorted([y1, y2])
                    cropped = frame[y1:y2, x1:x2]
                    filename = f"logs/photo_{timestamp}_roi{idx}.jpg"
                    cv2.imwrite(filename, cropped)
                    self.logger.log(timestamp, f"ROI {idx} photo captured: {filename}")
                    print(f"[Photo] Saved ROI {idx}: {filename}")
            else:
                # Save full frame if no ROI
                filename = f"logs/photo_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                self.logger.log(timestamp, f"Full-frame photo captured: {filename}")
                print(f"[Photo] Saved full-frame photo: {filename}")

    def toggle_recording(self):
        if not self.recording:
            filename = self.filename_entry.get()
            if not filename.endswith(".avi"):
                filename += ".avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter("footages/"+filename, fourcc, self.camera.frame_rate,
                                                (int(self.camera.cap.get(3)), int(self.camera.cap.get(4))))
            self.recording = True
            self.record_btn.config(text="Stop Recording")
            print(f"[Video] Recording started: {filename}")
        else:
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            self.record_btn.config(text="Start Recording")
            print("[Video] Recording stopped.")

    def toggle_interval_capture(self):
        if not self.interval_capture:
            try:
                interval = int(self.interval_entry.get())
                if interval <= 0:
                    raise ValueError
                self.interval_seconds = interval
                self.interval_capture = True
                self.interval_btn.config(text="Stop Interval Capture")
                print(f"[Timelapse] Interval photo capture started: every {interval} seconds")
                self.root.after(self.interval_seconds * 1000, self.capture_photo_interval)
            except ValueError:
                print("[System] Please enter a valid positive integer for interval.")
        else:
            self.interval_capture = False
            self.interval_btn.config(text="Start Interval Capture")
            print("[Timelapse] Interval photo capture stopped.")

    def capture_photo_interval(self):
        if self.interval_capture:
            self.take_photo()
            self.root.after(self.interval_seconds * 1000, self.capture_photo_interval)

    def clear_roi(self):
        self.roi_manager.clear_boxes()
        print("[System] All ROI boxes cleared.")

    def start_draw_roi(self, event):
        self.drawing_roi = True
        self.roi_start = (event.x, event.y)
        print(f"[Draw] Start ROI at {self.roi_start}")

    def update_draw_roi(self, event):
        if self.drawing_roi:
            self.temp_frame = self.current_frame.copy()
            cv2.rectangle(self.temp_frame, self.roi_start, (event.x, event.y), (255, 0, 0), 2)
            self.display_frame(self.temp_frame)

    def finish_draw_roi(self, event):
        if self.drawing_roi:
            roi_end = (event.x, event.y)
            self.roi_manager.add_box(self.roi_start, roi_end)
            print(f"[Draw] ROI added: {self.roi_start} to {roi_end}")
            self.drawing_roi = False
    def pick_target_color(self):
        """
        Enters color picking mode by pausing video feed and binding mouse click.
        """
        if not self.color_picking_mode:
            print("[Colors] Color Picking Mode: Click anywhere on the video feed to pick a color.")
            self.color_picking_mode = True

            # Temporarily disable ROI drawing
            self.video_label.unbind("<Button-1>")

            # Pause video updates
            self.paused_frame = self.current_frame.copy()
            self.display_frame(self.paused_frame)

            # Bind click for color picking
            self.video_label.bind("<Button-1>", self.get_color_from_click)

    def get_color_from_click(self, event):
        if self.color_picking_mode and self.paused_frame is not None:
            # Map click coords from widget to frame coords
            widget_width = self.video_label.winfo_width()
            widget_height = self.video_label.winfo_height()
            frame_height, frame_width = self.paused_frame.shape[:2]

            scale_x = frame_width / widget_width
            scale_y = frame_height / widget_height

            x = int(event.x * scale_x)
            y = int(event.y * scale_y)

            # Clamp coordinates
            x = max(0, min(frame_width - 1, x))
            y = max(0, min(frame_height - 1, y))

            # Get BGR color
            bgr_color = self.paused_frame[y, x]
            self.target_color = bgr_color
            print(f"[Colors] Selected Color at ({x}, {y}): BGR={bgr_color}")

            # Exit color picking mode
            self.color_picking_mode = False

            # Rebind ROI drawing
            self.video_label.bind("<Button-1>", self.start_draw_roi)

            # Resume video feed
            self.update_video()
            
    def toggle_color_monitoring(self):
        self.color_monitoring = not self.color_monitoring
        state = "ON" if self.color_monitoring else "OFF"
        self.color_btn.config(text=f"{'Stop' if self.color_monitoring else 'Start'} Color Monitoring")
        print(f"[Colors] Color monitoring turned {state}.")

    def toggle_object_monitoring(self):
        self.object_monitoring = not self.object_monitoring
        state = "ON" if self.object_monitoring else "OFF"
        self.object_btn.config(text=f"{'Stop' if self.object_monitoring else 'Start'} Object Monitoring")
        print(f"[Objects] Object monitoring turned {state}.")

    def update_video(self):
        if self.running and not self.color_picking_mode:
            frame, timestamp = self.camera.get_frame()
            if frame is not None:
                self.current_frame = frame.copy()
                self.roi_manager.draw_rois(frame)

                # Color monitoring
                if self.color_monitoring and self.target_color is not None:
                    for idx, (start, end) in enumerate(self.roi_manager.roi_boxes, start=1):
                        x1, y1 = start
                        x2, y2 = end
                        roi = self.current_frame[y1:y2, x1:x2]
                        try:
                            changed, mean_color = self.vision_utils.detect_color_change(roi, self.target_color)
                            if changed:
                                print(f"[Colors] ROI {idx}: Color changed! Mean BGR={mean_color}")
                        except Exception as e:
                            print(f"[Colors] Color monitoring error: {e}")


                # Object monitoring
                if self.object_monitoring:
                    for idx, (start, end) in enumerate(self.roi_manager.roi_boxes, start=1):
                        x1, y1 = start
                        x2, y2 = end
                        roi = self.current_frame[y1:y2, x1:x2]

                        try:
                            detections = self.vision_utils.detect_objects(roi)
                            if detections:
                                for det in detections:
                                    # Bounding box in ROI coordinates
                                    bx, by, bw, bh = det["box"]
                                    # Draw box on the main frame (offset by ROI position)
                                    cv2.rectangle(
                                        self.current_frame,
                                        (x1 + bx, y1 + by),
                                        (x1 + bx + bw, y1 + by + bh),
                                        (0, 255, 0),
                                        2
                                    )
                                    cv2.putText(
                                        self.current_frame,
                                        f"{det['label']} {det['confidence']:.2f}",
                                        (x1 + bx, y1 + by - 5),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.5,
                                        (0, 255, 0),
                                        2
                                    )
                                print(f"✅ ROI {idx}: Objects detected -> {[d['label'] for d in detections]}")
                            else:
                                print(f"⚠️ ROI {idx}: No object detected!")
                        except Exception as e:
                            print(f"⚠️ Object monitoring error: {e}")

                if self.recording and self.video_writer:
                    self.video_writer.write(frame)
                self.display_frame(frame)
        # Schedule next frame only if not in color picking mode
        
        if not self.color_picking_mode:
            self.root.after(int(1000 / self.camera.frame_rate), self.update_video)    

    def display_frame(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

    def start(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        print("[System] Closing application...")
        self.running = False
        self.interval_capture = False
        if self.recording and self.video_writer:
            self.video_writer.release()
        self.camera.release()
        self.root.destroy()
