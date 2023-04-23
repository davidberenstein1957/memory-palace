import logging
import os
import shutil
import threading
import uuid
import wave

import pyaudio

from memory_palace.processors import WhisperProcessor

_LOGGER = logging.getLogger(__name__)
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10

THREADING_LOCK = threading.Lock()


class AudioCapturer(threading.Thread):
    def __init__(self, processor: WhisperProcessor) -> None:
        super().__init__()
        self.processor = processor
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

            # acquire the lock
            THREADING_LOCK.acquire()

            # save raw audio as WAV file
            file = f"{self.processor.output_dir}/{uuid.uuid4()}.wav"
            waveFile = wave.open(file, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(self.audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()

            # release the lock
            THREADING_LOCK.release()

            self.processor.queue.put(file)

    def stop(self):
        # acquire the lock
        THREADING_LOCK.acquire()

        if not os.path.exists(self.processor.output_dir):
            shutil.rmtree(self.processor.output_dir)

        # release the lock
        THREADING_LOCK.release()

        self.running = False
        self.join()