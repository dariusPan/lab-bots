
# 📷 Experiment Monitoring Tool

A Python-based modular experiment monitoring system using **Logitech C920 Pro HD** webcam. Includes GUI, frame logging, and ROI tools for lab experiments.

---

## 🚀 Features
- ✅ **Live Video Feed** with GUI (Tkinter)
- ✅ **Configurable frame rate** or interval photo capture
- ✅ **Frame timestamping**
- ✅ **CSV Log System** for tracking events
- ✅ **Draw and monitor ROIs (Regions of Interest)**
- ✅ Modular architecture for adding **color detection, alarms**, etc.

---

## 📦 Setup

### 1️⃣ Install Requirements
Make sure Python 3.8+ is installed.  
Install dependencies:  
```bash
pip install opencv-python pillow
```

---

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/dariusPan/lab-bots.git
cd experiment-monitor
```

---

## 🖱 Draw ROI on Video Feed
1. Click and drag on the video feed to draw a rectangular ROI.
2. Release mouse button to confirm the ROI.
3. Multiple ROIs can be added.
4. Click “Clear ROI” to remove all ROIs.

---

### 3️⃣ Run the App
```bash
python main.py
```

---

## 🎥 Recording Videos
1. Enter a filename (e.g., `experiment.avi`) in the input box.
2. Press **Start Recording**.
3. Press **Stop Recording** to save the video.

---

## 🛠 Configuration
Edit `config.py` to customize:
- **Frame Rate**: `FRAME_RATE = 15`
- **Photo Interval**: `CAPTURE_INTERVAL = 5`
- **ROI Color**: `ROI_COLOR = (0, 255, 0)`

---

## 🎨 ROI Management
- ROIs are predefined in `main.py`.
- To add ROIs:
```python
roi_manager.add_box((x1, y1), (x2, y2))
```

---

## 📝 Logging
Logs are saved in:
```
logs/experiment_log.csv
```
Each photo taken is timestamped and logged.

---

## 🛡 Modular Design
Add your own modules for:
- 📐 **Advanced ROI shapes**
- 🎨 **Color monitoring**
- 🚨 **Alarm triggers**
