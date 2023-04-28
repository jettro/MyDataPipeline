import json
from logging import config

from dotenv import load_dotenv

from log_config import logging_config

from util import SimplePipeline, LogInputPipelineStep
from weaviatedb import WeaviateClient
from weaviatedb.query_for_products_pipeline_step import QueryForProductsPipelineStep

from reranking import ReorderQueryPipelineStep

load_dotenv()  # take environment variables from .env.
config.dictConfig(logging_config)

if __name__ == '__main__':
    weaviate_client = WeaviateClient()

    steps = [
        LogInputPipelineStep(name="Log the name step"),
        QueryForProductsPipelineStep(name="Query Weaviate", weaviate_client=weaviate_client)
    ]
    pipeline = SimplePipeline(steps=steps)
    response = pipeline.start_process(input_data={"search_text": "high heal"})

    # response = step.execute_step({"search_text": "high heals"})

    # weaviate_client.delete_class("Product")
    # weaviate_client.create_classes("./config_files/product_schema.json")
    # print(json.dumps(weaviate_client.get_schema(), indent=4))
    # weaviate_client.load_data()
    # response = weaviate_client.query("high heal")
    # output_data = {"result_items": response["data"]["Get"]["Product"]}

    print(json.dumps(response, indent=4))
