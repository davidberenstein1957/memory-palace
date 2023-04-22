import mailbox

import dateparser
from bs4 import BeautifulSoup
from haystack import Document
from tqdm import tqdm


class GMailToText(object):
    def __init__(self) -> None:
        pass

    def mbox_to_documents(self, path_to_mbox: str) -> str:
        mbox = mailbox.mbox(path_to_mbox)
        documents = [self.message_to_document(message) for message in tqdm(mbox, desc="Converting mbox to documents", total=len(mbox))]
        return documents


    def message_to_document(self, message):
        message_id = message['Message-Id']
        subject = message['subject']
        _from = message['from']
        _to = message['to']
        data = dateparser.parse(message['date'])
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
                id=f"email_gmail_{message_id}",
                content=body,
                meta={
                    "source_type": "email",
                    "source_subtype": "gmail",
                    "source_id": message_id,
                    "subject": subject,
                    "from": _from,
                    "to": _to,
                    "date": data,
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