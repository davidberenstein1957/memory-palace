import logging

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)

from haystack import Pipeline
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import (
    BM25Retriever,
    EmbeddingRetriever,
    FARMReader,
    PreProcessor,
    SklearnQueryClassifier,
)

# This is a default usage of the PreProcessor.
# Here, it performs cleaning of consecutive whitespaces
# and splits a single large document into smaller documents.
# Each document is up to 1000 words long and document breaks cannot fall in the middle of sentences
# Note how the single document passed into the document gets split into 5 smaller documents


document_store = ElasticsearchDocumentStore(
    similarity="dot_product",
    embedding_dim=384
)
preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=False,
    split_respect_sentence_boundary=False,
    split_overlap=3,
    split_by="sentence",
    split_length=10,
)
embedding_retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="multi-qa-MiniLM-L6-cos-v1",
    use_gpu=True,
    model_format="sentence_transformers"
)
bm25_retriever = BM25Retriever(document_store=document_store)
farm_reader = FARMReader(model_name_or_path="deepset/xlm-roberta-base-squad2")
keyword_classifier = SklearnQueryClassifier()

str_indexing_pipeline = Pipeline()
str_indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["File"])
str_indexing_pipeline.add_node(component=embedding_retriever, name="EmbeddingRetriever", inputs=["PreProcessor"])
str_indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["EmbeddingRetriever"])


keyword_classifier_pipeline = Pipeline()
keyword_classifier_pipeline.add_node(component=keyword_classifier, name="QueryClassifier", inputs=["Query"])
keyword_classifier_pipeline.add_node(
    component=embedding_retriever, name="EmbeddingRetriever", inputs=["QueryClassifier.output_1"]
)
keyword_classifier_pipeline.add_node(component=bm25_retriever, name="BM25Retriever", inputs=["QueryClassifier.output_2"])
keyword_classifier_pipeline.add_node(component=farm_reader, name="QAReader", inputs=["BM25Retriever", "EmbeddingRetriever"])

