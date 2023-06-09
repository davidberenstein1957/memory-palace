import logging
import queue
import threading
import time
from typing import Union

from haystack import Document

from memory_palace.pipelines.haystack_pipelines import str_indexing_pipeline

SLEEP_INTERVAL = 60
_LOGGER = logging.getLogger(__name__)

class HaystackIndexer(threading.Thread):
    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()
        self.running = False
        self.queue = queue.Queue()

    def run(self):
        self.running = True
        while self.running:
            documents_batch = []

            while ((not self.queue.empty()) and (len(documents_batch) < 1000)):
                item = self.queue.get()
                documents_batch.append(item)

            if len(documents_batch) > 0:
                _LOGGER.info(f"Processing {len(documents_batch)} documents")
                str_indexing_pipeline.run(documents=documents_batch)
            time.sleep(SLEEP_INTERVAL)


    def stop(self):
        self.running = False
        self.join()

    def add_documents(self, documents: Union[list[Document], Document]):
        if isinstance(documents, Document):
            documents = [documents]
        for document in documents:
            self.queue.put(document)
