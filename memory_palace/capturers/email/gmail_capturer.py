import logging
import mailbox
import threading

import dateparser
from bs4 import BeautifulSoup
from haystack import Document
from tqdm import tqdm

_LOGGER = logging.getLogger(__name__)


class GmailCapturer(threading.Thread):
    def __init__(self, processor, type="audio", subtype="whisper") -> None:
        super().__init__()
        self.processor = processor
        self.type = type
        self.subtype = subtype
        self.running = False

    def run(self):
        _LOGGER.info("Started Runing...")
        self.running = True
        while self.running:
            pass

    def stop(self):
        _LOGGER.info("Stopped Running.")
        self.running = False
        self.join()

    def mbox_to_documents(self, path_to_mbox: str) -> str:
        _LOGGER.info("Started converting mbox to documents...")
        mbox = mailbox.mbox(path_to_mbox)
        for message in tqdm(mbox, desc="Converting mbox to documents", total=len(mbox)):
            self.processor.document_queue.put(self.message_to_document(message))


    def message_to_document(self, message):
        message_id = message['Message-Id']
        subject = message['subject']
        _from = message['from']
        _to = message['to']
        date = message['date']
        if isinstance(date, str):
            date = dateparser.parse(message['date'])
        body = self.get_message_body(message)
        if body is None:
            print("ERROR")
        else:
            if _to is not None:
                _to = _to.lower().split()
            if _from is not None:
                _from = _from.lower().split()
            if subject is not None:
                subject = subject.lower().split()
            return Document(
                id=f"{self.type}_{self.subtype}_{message_id}",
                content=body,
                meta={
                    "source_type": self.type,
                    "source_subtype": self.subtype,
                    "source_id": message_id,
                    "subject": subject,
                    "from": _from,
                    "to": _to,
                    "date": date,
                }
            )

    def get_message_body(self, message): # getting plain text 'email body'
        body = None
        if message.is_multipart():
            for part in message.walk():
                if part.is_multipart():
                    for subpart in part.walk():
                        if subpart.get_content_type() == 'text/plain':
                            body = subpart.get_payload(decode=True)
                elif part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True)
                elif part.get_content_type() == 'text/html':
                    body = BeautifulSoup(part.get_payload(decode=True), "lxml").text
        elif message.get_content_type() == 'text/plain':
            body = message.get_payload(decode=True)
        elif message.get_content_type() == 'text/html':
            body = BeautifulSoup(message.get_payload(decode=True), "lxml").text

        return body