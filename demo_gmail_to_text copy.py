from src import str_indexing_pipeline
from src.email_to_text.gmail import GMailToText

documents = GMailToText().mbox_to_documents('data/All mail Including Spam and Trash.mbox')

str_indexing_pipeline.run(documents=documents)