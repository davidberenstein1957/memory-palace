

# Memory Palace

An open-source and privacy-friendly memory-palace for the pragmatic programmer.

## Components

`memory-palace` differentiates between several components that handle different parts of the creation of your personal memory palace. They handle your incoming memories sequentially and ought to be used in a pipeline-like fashion. Note that you can for example pass manually captured audio

1. `Capturers` are programatically capturing memories from different sources in different formats like audio, email, chat, and image.
2. `Processors` periodically process the captured memories from each of the formats and converts them to `haystack.Documents`. For example, audio is transcribed to text and OCR is run on images.
3. `Indexers` as of now we only support one indexer, the `HaystackIndexer`, which uses `ElasticSearch` to create a semantic index for your processed `haystack.Document`.
4. `pipelines` are pipelines to index documents into `haystack` and compose queries. Note that I am also using `argilla` to keep track of used queries and train NLP models to help with fine-tuning query results.

Lastly, I offer a `FastAPI` application to add manual input to `Processor` (think spoken or written dictates via Apple shortcuts, or written text images to be OCRed), check the status of running components, and query your memory palace. Later on, I will look into a nicer UI. Note that this FastAPI can also be used to run certain components locally to, for example, capture audio and screenshots, and run other more compute heavy components in the cloud.

### Capturers

- The default `AudioCapturer` uses the `pyaudio` and `wave` to capture audio fragments and save them as `.wav`-files, which are then stored in the `queue` of the `WhisperProcessor`.
- The default `WhatsAppCapturer` uses icloud exports to
- The default `GmailCapturer` uses the google SDK to load emails from a certain start-date and add them to the `EmailProcessor`.
- The default `ScreenCapturer` uses the `pillow.ImageGrab` to take screenshots and add them to the `EasyOCRProcessor`.

I want to work towards adding support for `SlackCapturer`, `ApplicationCapturer`, `WebsiteCapturer`.

### Processors

- The `EmailProcessor` takes `.mbox` files or individual `.mail` message and adds them to the `HaystackIndexer` as `haystack.Documents`.
- The `WhisperProcessor` converts `.wav` files to text and adds them to the `HaystackIndexer` as `haystack.Documents`.
- The `EasyOCRProcessor` converts `images` to text using `easyocr` and adds them to the `HaystackIndexer` as `haystack.Documents`.

### Pipelines

- The `string_indexing_pipeline` uses a `PreProcessor` to format string to and splitup documents, and a `EmbeddingRetriever` to add qa and semantic embeddings to the `haystack.Document`.
- The `keyword_classifier_pipeline` is a query pipeline which uses an `sklearn` classifier to either do a semantic search, QnA search or a keyword based search.

I want to work towards several TokenClassification and TextClassification pipelines, which can be used to further fine-tune filter passed to the query pipeline. For example, "What did I discuss with Daniel last week?" ought to pick up (last week, DATE) and (Daniel, PERSON), which can be used as filters. These predictions and fine-tunes should be logged into `argilla`.

### Indexers

The `HaystackIndexer` indexes document using a `pipeline`, which by default uses the `string_indexing_pipeline`.


## NOTES

on mac requirements audio
- brew install portaudio

extras audio
- pyaudio
- wave (internal)

extras ocr
- easyocr

email
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib
- beautifulsoup4

later API
[Google Takeout](https://takeout.google.com/) for mail and calendar items

[Whatsapp backupp](https://faq.whatsapp.com/1180414079177245/?locale=fi_FI&cms_platform=android)

## TODOs

- [] QnA - cheap inference images
- [] Embedding - cheap inference images
- [] Tokens - Crosslingual FewNERD
- [] Keywords - Crosslingual
- [] Images - [clip embeddingsdoc](https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1)


- [] Chat data [text, speaker, time, person, thread, persons] [thread, persons]
  - [] Whatsapp
  - [] Email
  - [] Slack
- [] Mono data [source, text, time, segement_id/sentence/paragraph] [source, summary] []
  - Articles
  - Websites
  - Voice messages/memos [whisper](https://github.com/ahmetoner/whisper-asr-webservice)

- elasticsearch
- pcloud backups