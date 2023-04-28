import logging
from copy import deepcopy

from util import PipelineStep
from weaviatedb import WeaviateClient


class QueryForProductsPipelineStep(PipelineStep):

    def __init__(self, name: str, weaviate_client: WeaviateClient):
        super().__init__(name)
        self.logger = logging.getLogger("weaviate")
        self.weaviate_client = weaviate_client

    def execute_step(self, input_data):
        query_text = input_data["search_text"]
        self.logger.info(f"Execute the query for search text {query_text}")

        response = self.weaviate_client.query(query_text=query_text)
        output_data = deepcopy(input_data)
        output_data["result_items"] = response["data"]["Get"]["Product"]

        return output_data
