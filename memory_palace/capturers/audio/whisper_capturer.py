
import datetime
import logging
import os
import queue
import shutil
import threading
import uuid
import wave

import pyaudio
import requests
from haystack import Document

_LOGGER = logging.getLogger(__name__)
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
tmp_dir = "tmp_data/audio/whisper_capturer"
WAVE_OUTPUT_FILENAME = "output.wav"



class AudioCapturer(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.writing_lock = threading.Lock()
        self.queue = queue.Queue()
        self.idx = 0
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.audio = pyaudio.PyAudio()
            stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)

            frames = []

            _LOGGER.info("Recording...")
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            _LOGGER.info("Recording finished.")

            # stop recording audio
            stream.stop_stream()
            stream.close()
            self.audio.terminate()

            # save raw audio as WAV file
            # acquire the lock
            self.writing_lock.acquire()
            # open file for appending
            file = f"{tmp_dir}{uuid.uuid4()}.wav"
            waveFile = wave.open(file, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(self.audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()
            # release the lock
            self.writing_lock.release()

            self.queue.put(file)

    def stop(self):
        if not os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        self.running = False
        self.join()

class WhisperCapturer(threading.Thread):
    def __init__(self, processor, type="audio", subtype="whisper") -> None:

        # Path(tmp_dir).mkdir(parents=True, exist_ok=True)
        super().__init__()
        self.audio_capturer = AudioCapturer()
        self.audio_capturer.start()
        self.processor = processor
        self.type = type
        self.subtype = subtype
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            while not self.audio_capturer.queue.empty():
                file = self.audio_capturer.queue.get()
                self.process_file(file)
                os.remove(file)

    def stop(self):
        self.audio_capturer.stop()
        self.running = False
        self.join()

    def process_file(self, file: str):
        url = "http://localhost:9000/asr?task=transcribe&output=json&language=en&method=faster-whisper&encode=true"
        with open(file, 'rb') as f:
            files = {'audio_file': (file, f)}
            response = requests.post(url, files=files)
        document = self.response_to_document(response)
        if document is not None:
            self.processor.add_documents(document)

    def response_to_document(self, response):
        json_payload = response.json()
        if json_payload['text']:
            return Document(
                content=json_payload['text'].strip(),
                meta={
                    "source_type": self.type,
                    "source_subtype": self.subtype,
                    "date": datetime.datetime.now(),
                }
            )


        # return Document(
        #     response.json()
        # )