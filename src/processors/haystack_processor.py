import queue
import threading
import time
from typing import Union

from haystack import Document

SLEEP_INTERVAL = 60

class HaystackProcessor(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.running = False
        self.document_queue = queue.Queue()

    def run(self):
        self.running = True
        while self.running:
            documents_batch = []

            while not self.document_queue.empty():
                item = self.document_queue.get()
                documents_batch.append(item)

            if len(documents_batch) > 0:

            time.sleep(SLEEP_INTERVAL)


    def stop(self):
        self.running = False
        self.join()

    def add_documents(self, documents: Union[list[Document], Document]):
        if isinstance(documents, Document):
            documents = [documents]
        for document in documents:
            self.document_queue.put(document)
