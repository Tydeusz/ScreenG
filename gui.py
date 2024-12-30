import sys
from threading import Thread
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QStatusBar, QComboBox
from PyQt5.QtGui import QPalette, QColor

from audio_recorder import AudioRecorder
from video_recorder import VideoRecorder

class ScreenAudioRecorder(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Screen and Audio Recorder")
        self.setGeometry(100, 100, 400, 300)

        # Apply Dark Mode with Neon Accents
        self.apply_dark_mode()

        # UI Elements
        self.output_path_label = QtWidgets.QLabel("Output Path:")
        self.output_path_input = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.audio_device_label = QtWidgets.QLabel("Audio Device:")
        self.audio_device_selector = QComboBox()
        self.audio_only_checkbox = QtWidgets.QCheckBox("Audio Only")
        self.start_button = QtWidgets.QPushButton("Start Recording")
        self.stop_button = QtWidgets.QPushButton("Stop Recording")
        self.status_bar = QStatusBar()

        # Apply rounded buttons
        self.style_buttons()

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.output_path_label)
        layout.addWidget(self.output_path_input)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.audio_device_label)
        layout.addWidget(self.audio_device_selector)
        layout.addWidget(self.audio_only_checkbox)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_bar)
        self.setLayout(layout)

        # Connections
        self.browse_button.clicked.connect(self.browse_output_path)
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.audio_device_selector.currentIndexChanged.connect(self.update_audio_device)

        # Flags and Variables
        self.recording = False
        self.audio_thread = None
        self.video_thread = None

        # Recorder Instances
        self.audio_recorder = AudioRecorder()
        self.video_recorder = VideoRecorder()

        # Initially disable the stop button
        self.stop_button.setEnabled(False)

        # Populate audio devices
        self.populate_audio_devices()

    def apply_dark_mode(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(200, 200, 200))
        palette.setColor(QPalette.Base, QColor(20, 20, 20))
        palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(200, 200, 200))
        palette.setColor(QPalette.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ButtonText, QColor(200, 200, 200))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)

    def style_buttons(self):
        button_style = (
            "QPushButton {"
            "    background-color: #007ACC;"
            "    color: white;"
            "    border-radius: 10px;"
            "    padding: 8px;"
            "    font-size: 14px;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #005F9E;"
            "}"
        )
        self.browse_button.setStyleSheet(button_style)
        self.start_button.setStyleSheet(button_style)
        self.stop_button.setStyleSheet(button_style)

    def browse_output_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_path_input.setText(path)
            self.update_status("Output path selected: " + path)

    def start_recording(self):
        output_path = self.output_path_input.text()
        if not output_path:
            self.update_status("Error: No output directory selected.")
            return

        if self.audio_device_selector.currentIndex() == -1:
            self.update_status("Error: No audio device selected.")
            return

        audio_only = self.audio_only_checkbox.isChecked()

        self.recording = True
        self.update_status("Recording started.")

        self.audio_recorder.audio_device_index = self.audio_device_selector.itemData(
            self.audio_device_selector.currentIndex()
        )
        self.audio_recorder.start_recording(output_path)

        self.audio_thread = Thread(target=self.audio_recorder.record_audio)
        self.audio_thread.start()

        if not audio_only:
            self.video_recorder.start_recording(output_path)
            self.video_thread = Thread(target=self.video_recorder.record_screen)
            self.video_thread.start()

        self.start_button.setText("Recording...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        self.audio_recorder.stop_recording()
        if self.video_recorder.recording:
            self.video_recorder.stop_recording()

        if self.audio_thread:
            self.audio_thread.join()
        if self.video_thread:
            self.video_thread.join()

        self.update_status("Recording stopped.")
        self.start_button.setText("Start Recording")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def populate_audio_devices(self):
        from pyaudio import PyAudio

        p = PyAudio()
        self.audio_device_selector.clear()
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                self.audio_device_selector.addItem(device_info['name'], userData=i)
        if self.audio_device_selector.count() > 0:
            self.audio_device_selector.setCurrentIndex(0)
        else:
            self.update_status("No audio input devices found.")
        p.terminate()

    def update_audio_device(self, index):
        self.audio_recorder.audio_device_index = self.audio_device_selector.itemData(index)
        self.update_status(f"Audio device set to: {self.audio_device_selector.currentText()}")

    def update_status(self, message):
        self.status_bar.showMessage(message)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ScreenAudioRecorder()
    window.show()
    sys.exit(app.exec_())
