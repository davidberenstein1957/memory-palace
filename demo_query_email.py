from src import keyword_classifier_pipeline

filters = {"filters": {'subject': {"$in": ['f5bot']}}}
print(keyword_classifier_pipeline.run("What did the f5bot find?", params={"BM25Retriever": filters, "EmbeddingRetriever": filters}))
