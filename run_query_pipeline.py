import json
from logging import config

from dotenv import load_dotenv

from log_config import logging_config
from search import QueryPipeline, LogInputPipelineStep, ReorderQueryPipelineStep, RerankCrossencoderPipelineStep
from weaviatedb.weaviate_client import CallWeaviatePipelineStep

load_dotenv()  # take environment variables from .env.
config.dictConfig(logging_config)


if __name__ == '__main__':
    steps = [
        LogInputPipelineStep(name="Log the name step"),
        CallWeaviatePipelineStep(name="Query Weaviate"),
        RerankCrossencoderPipelineStep(name="Rerank using cross encoder")
        # ReorderQueryPipelineStep(name="Reorder using cross encoder")
    ]
    pipeline = QueryPipeline(steps=steps)
    response = pipeline.start_process(input_data={"search_text": "much like a crocodile"})
    print(json.dumps(response, indent=4))
