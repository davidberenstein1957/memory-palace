from haystack import Pipeline
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import EmbeddingRetriever, PreProcessor

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
    split_by="sentence",
    split_length=100,
    split_respect_sentence_boundary=True,
)
retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="multi-qa-MiniLM-L6-cos-v1",
    use_gpu=True,
    model_format="sentence_transformers"
)

str_indexing_pipeline = Pipeline()
str_indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["Document"])
str_indexing_pipeline.add_node(component=retriever, name="EmbeddingRetriever", inputs=["PreProcessor"])
str_indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["EmbeddingRetriever"])