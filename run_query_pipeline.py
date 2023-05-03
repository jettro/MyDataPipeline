import json
from logging import config

from dotenv import load_dotenv

from log_config import logging_config

from util import LogInputPipelineStep, SimplePipeline
from weaviatedb import WeaviateClient, InitializeProductsInWeaviatePipelineStep, QueryForProductsPipelineStep
from reranking import RerankCrossencoderPipelineStep

load_dotenv()  # take environment variables from .env.
config.dictConfig(logging_config)

if __name__ == '__main__':
    weaviate_client = WeaviateClient()
    steps = [
        LogInputPipelineStep(name="Log the name step"),
        InitializeProductsInWeaviatePipelineStep(name="Initialize data in Weaviate",
                                                 weaviate_client=weaviate_client,
                                                 enabled=False),
        QueryForProductsPipelineStep(name="Query Weaviate", weaviate_client=weaviate_client),
        RerankCrossencoderPipelineStep(name="Rerank using cross encoder")
    ]
    pipeline = SimplePipeline(steps=steps)
    response = pipeline.start_process(input_data={"search_text": "high heal"})
    print(json.dumps(response, indent=4, default=float))
