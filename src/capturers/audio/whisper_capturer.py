
import threading
import wave

import pyaudio
import requests

FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"
MP3_OUTPUT_FILENAME = "output.mp3"



class WhisperCapturer(threading.Thread):
    def __init__(self, type="audio", subtype="whisper") -> None:
        super().__init__()
        self.type = type
        self.subtype = subtype
        self.audio = pyaudio.PyAudio()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)

            frames = []

            print("Recording...")
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            print("Recording finished.")

            # stop recording audio
            stream.stop_stream()
            stream.close()
            self.audio.terminate()

            # save raw audio as WAV file
            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(self.audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()

            url = "http://localhost:9000/asr?task=transcribe&output=json&language=en&method=faster-whisper&encode=true"
            with open(WAVE_OUTPUT_FILENAME, 'rb') as f:
                files = {'audio_file': (MP3_OUTPUT_FILENAME, f)}
                response = requests.post(url, files=files)

            print(response.json())

    def stop(self):
        self.running = False
        self.join()

    def response_to_document(self, response):
        pass