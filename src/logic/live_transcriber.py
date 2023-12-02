import os
import re
import threading
import queue

import sounddevice as sd
from .. import whisper
from scipy.io.wavfile import write


class LiveTranscriber:
    def __init__(self):
        self.audio_file_name = "temp.wav"
        self.model = whisper.load_model("base")
        self.language = "english"
        self.transcription_queue = queue.Queue()
        self.recording_complete = threading.Event()
        self.stop_recording = threading.Event()

    def start_transcription_thread(self):
        transcription_thread = threading.Thread(target=self.transcribe_loop)
        transcription_thread.start()

    def transcribe_loop(self):
        while not self.stop_recording.is_set():
            self.recording_complete.wait()
            transcribed_text = self.transcribe()
            self.transcription_queue.put(transcribed_text)
            self.recording_complete.clear()

    def start_recording_thread(self):
        recording_thread = threading.Thread(target=self.record_loop)
        recording_thread.start()

    def record_loop(self):
        while not self.stop_recording.is_set():
            self.recorder()
            self.recording_complete.set()
            self.stop_recording.wait(2)

    def start_live_transcription(self):
        self.start_recording_thread()
        self.start_transcription_thread()

    def stop_live_transcription(self):
        if os.path.exists(self.audio_file_name):
            os.remove(self.audio_file_name)
        self.stop_recording.set()

    def transcribe(self):
        print("Transcribing...")

        result = self.model.transcribe(audio=self.audio_file_name, cancel_func=self.cancel_callback)
        cleaned_result = self.clean_transcription(result['text'])
        print(f"Result: {cleaned_result}")

        os.remove(self.audio_file_name)

        return cleaned_result

    def recorder(self, duration=5):
        print("Say something...")
        sample_rate = 44100
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2)
        sd.wait()

        write(self.audio_file_name, sample_rate, recording)

        print(f"Recording saved as {self.audio_file_name}")

    def cancel_callback(self):
        pass

    @staticmethod
    def clean_transcription(transcription):
        cleaned_text = re.sub(r'[^a-zA-Z\s]', '', transcription).strip()
        return cleaned_text


# transcriber = LiveTranscriber()
# transcriber.start_live_transcription()
# transcriber.stop_live_transcription()
