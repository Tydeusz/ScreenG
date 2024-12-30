import os
import cv2
import numpy as np
import mss
from PyQt5.QtWidgets import QDesktopWidget

class VideoRecorder:
    def __init__(self):
        self.video_filename = None
        self.recording = False

    def start_recording(self, output_path):
        self.recording = True
        screen_geometry = QDesktopWidget().screenGeometry()
        self.screen_size = (screen_geometry.width(), screen_geometry.height())

        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # MP4 encoding
        self.video_filename = os.path.join(output_path, "output.mp4")

        self.out = cv2.VideoWriter(self.video_filename, fourcc, 20.0, self.screen_size)

    def record_screen(self):
        # Create a new mss instance here to ensure thread safety
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Capture the first monitor

            try:
                while self.recording:
                    screenshot = sct.grab(monitor)
                    frame = np.array(screenshot)[:, :, :3]  # Convert BGRA to BGR
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    frame = cv2.resize(frame, self.screen_size)
                    self.out.write(frame)
            finally:
                self.stop_recording()

    def stop_recording(self):
        self.recording = False
        if self.out:
            self.out.release()

    def get_video_filename(self):
        return self.video_filename
