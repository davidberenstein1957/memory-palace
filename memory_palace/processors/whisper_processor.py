
import datetime
import logging
import os
import queue
import threading
from pathlib import Path

import requests
from haystack import Document

from memory_palace.indexers import HaystackIndexer

_LOGGER = logging.getLogger(__name__)

THREADING_LOCK = threading.Lock()



class WhisperProcessor(threading.Thread):
    def __init__(self,
            indexer: HaystackIndexer,
            output_dir: str = "data/audio/whisper_capturer",
            type="audio",
            subtype="whisper"
        ) -> None:
        super().__init__()

        self.indexer = indexer
        self.output_dir = output_dir

        # acquire the lock
        THREADING_LOCK.acquire()
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        THREADING_LOCK.release()

        self.queue = queue.Queue()

        self.type = type
        self.subtype = subtype
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            while not self.queue.empty():
                file = self.queue.get()
                self.process_file(file)
                os.remove(file)

    def stop(self):
        self.running = False
        self.join()

    def process_file(self, file: str):
        url = "http://localhost:9000/asr?task=transcribe&output=json&language=en&method=faster-whisper&encode=true"

        # acquire the lock
        THREADING_LOCK.acquire()

        with open(file, 'rb') as f:
            files = {'audio_file': (file, f)}
            response = requests.post(url, files=files)

        # release the lock
        THREADING_LOCK.release()

        document = self.response_to_document(response)
        if document is not None:
            self.indexer.add_documents(document)

    def response_to_document(self, response):
        json_payload = response.json()
        if json_payload['text']:
            text = json_payload['text'].strip()
            issues = ["Thank you for watching.", "Thanks for watching!", "Thanks for watching.", "Thanks for watching.", "Thank you very much.", "You", "you", "thank you", "thank you.", "Thank you for watching!"]
            if text in issues:
                return None
            else:
                print(text)
            return Document(
                content=json_payload['text'].strip(),
                meta={
                    "source_type": self.type,
                    "source_subtype": self.subtype,
                    "date": datetime.datetime.now(),
                }
            )
