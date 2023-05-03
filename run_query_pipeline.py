import json
from logging import config

from dotenv import load_dotenv

from log_config import logging_config

from util import LogInputPipelineStep, SimplePipeline
from weaviatedb import WeaviateClient, InitializeProductsInWeaviatePipelineStep, QueryForProductsPipelineStep
from reranking import RerankCrossencoderPipelineStep, ReorderQueryPipelineStep

load_dotenv()  # take environment variables from .env.
config.dictConfig(logging_config)


def compare_results(response):
    results = response["result_items"]
    reordered = response["result_items_reranked"]

    for i in range(0, len(results)):
        print(f"name {results[i]['name'].ljust(35)}, name {reordered[i]['input']['name'].ljust(35)}, "
              f"score {reordered[i]['score']}")


if __name__ == '__main__':
    weaviate_client = WeaviateClient()
    steps = [
        LogInputPipelineStep(name="Log the name step"),
        InitializeProductsInWeaviatePipelineStep(name="Initialize data in Weaviate",
                                                 weaviate_client=weaviate_client,
                                                 enabled=False),
        QueryForProductsPipelineStep(name="Query Weaviate", weaviate_client=weaviate_client),
        ReorderQueryPipelineStep(name="Reorder results", enabled=False),
        RerankCrossencoderPipelineStep(name="Rerank using cross encoder")
    ]
    pipeline = SimplePipeline(steps=steps)
    response = pipeline.start_process(input_data={"search_text": "high heal"})
    # print(json.dumps(response, indent=4, default=float))
    compare_results(response)
