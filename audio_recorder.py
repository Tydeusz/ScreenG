import os
import pyaudio
import wave
from threading import Lock


class AudioRecorder:
    def __init__(self, audio_device_index=None):
        self.audio_device_index = audio_device_index
        self.audio_filename = None
        self.recording = False
        self.lock = Lock()
        self.stream = None
        self.wf = None
        self.p = None

    def start_recording(self, output_path):
        self.audio_filename = os.path.join(output_path, "output.wav")
        self.recording = True

        chunk = 1024  # Number of frames per buffer
        format = pyaudio.paInt16  # 16-bit resolution
        channels = 2  # Stereo
        rate = 44100  # 44.1 kHz sample rate

        self.p = pyaudio.PyAudio()

        try:
            self.stream = self.p.open(
                format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk,
                input_device_index=self.audio_device_index
            )
            self.wf = wave.open(self.audio_filename, 'wb')
            self.wf.setnchannels(channels)
            self.wf.setsampwidth(self.p.get_sample_size(format))
            self.wf.setframerate(rate)
        except Exception as e:
            self.stop_recording()
            raise RuntimeError(f"Failed to start audio recording: {str(e)}")

    def record_audio(self):
        if not self.recording or not self.stream or not self.wf:
            return

        chunk = 1024
        frames = []

        try:
            while self.recording:
                data = self.stream.read(chunk, exception_on_overflow=False)
                frames.append(data)

            if self.wf:
                self.wf.writeframes(b''.join(frames))
        except Exception as e:
            print(f"Error during audio recording: {e}")
        finally:
            self.stop_recording()

    def stop_recording(self):
        with self.lock:
            self.recording = False

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"Error closing audio stream: {e}")

        if self.wf:
            try:
                self.wf.close()
            except Exception as e:
                print(f"Error closing wave file: {e}")

        if self.p:
            try:
                self.p.terminate()
            except Exception as e:
                print(f"Error terminating PyAudio: {e}")

    def get_audio_filename(self):
        return self.audio_filename
