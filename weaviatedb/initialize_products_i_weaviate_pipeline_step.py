import logging
from copy import deepcopy

from util import PipelineStep
from weaviatedb import WeaviateClient


class InitializeProductsInWeaviatePipelineStep(PipelineStep):
    def __init__(self, name: str, weaviate_client: WeaviateClient, enabled: bool = True):
        super().__init__(name, enabled=enabled)
        self.weaviate_client = weaviate_client
        self.logger = logging.getLogger("weaviate")

    def execute_step(self, input_data):
        if not self.enabled:
            self.logger.info(f"Step {self.name} is disabled.")
            return input_data

        self.weaviate_client.delete_class("Product")
        self.weaviate_client.create_classes("./config_files/product_schema.json")
        schema = self.weaviate_client.get_schema()
        self.logger.info(schema)
        self.weaviate_client.load_data()

        output_data = deepcopy(input_data)
        output_data["created_schema"] = schema

        return output_data
