import csv
import os

class Logger:
    def __init__(self, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.file_path = file_path
        if not os.path.exists(file_path):
            with open(self.file_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Timestamp", "Event"])

    def log(self, timestamp, event):
        try:
            with open(self.file_path, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([timestamp, event])
        except IOError as e:
            print(f"Logger error: {e}")
