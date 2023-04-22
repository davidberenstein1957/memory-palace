from src import str_indexing_pipeline
from src.capturers.email.gmail_capturer import GmailCapturer

documents = GmailCapturer().mbox_to_documents('data/All mail Including Spam and Trash.mbox')

str_indexing_pipeline.run(documents=documents)p