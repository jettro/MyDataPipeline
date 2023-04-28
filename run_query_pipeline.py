import json
from logging import config

from dotenv import load_dotenv

from log_config import logging_config
from reranking import RerankCrossencoderPipelineStep
from util import LogInputPipelineStep, SimplePipeline
from weaviatedb import WeaviateClient
from weaviatedb.query_for_products_pipeline_step import QueryForProductsPipelineStep

load_dotenv()  # take environment variables from .env.
config.dictConfig(logging_config)


if __name__ == '__main__':
    weaviate_client = WeaviateClient()
    steps = [
        LogInputPipelineStep(name="Log the name step"),
        QueryForProductsPipelineStep(name="Query Weaviate", weaviate_client=weaviate_client),
        RerankCrossencoderPipelineStep(name="Rerank using cross encoder")
        # ReorderQueryPipelineStep(name="Reorder using cross encoder")
    ]
    pipeline = SimplePipeline(steps=steps)
    response = pipeline.start_process(input_data={"search_text": "high heal"})
    print(json.dumps(response, indent=4, default=float))
