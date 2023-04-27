import os
from copy import deepcopy

import weaviate
import requests
import json
import logging

from dotenv import load_dotenv

from search import PipelineStep

load_dotenv()  # take environment variables from .env.

auth_config = weaviate.auth.AuthApiKey(
    api_key=os.getenv('WEAVIATE_API_KEY'),
)

weaviate_log = logging.getLogger("weaviate")


class WeaviateClient:
    def __init__(self):
        self.client = weaviate.Client(
            url=os.getenv('WEAVIATE_URL'),
            auth_client_secret=auth_config,
            additional_headers={
                "X-OpenAI-Api-Key": os.getenv('OPEN_AI_API_KEY')
            }
        )

        weaviate_log.info(f"Weaviate client is connected: {self.client.is_ready()}")

    def get_schema(self):
        return self.client.schema.get()

    def create_classes(self):
        class_obj = {
            "class": "Question",
            "vectorizer": "text2vec-openai"
        }

        self.client.schema.create_class(class_obj)

    def load_data(self):
        url = 'https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/jeopardy_tiny.json'
        resp = requests.get(url)
        data = json.loads(resp.text)

        # Configure a batch process
        with self.client.batch as batch:
            batch.batch_size = 100
            # Batch import all Questions
            for i, d in enumerate(data):
                weaviate_log.info(f"importing question: {i + 1}")

                properties = {
                    "answer": d["Answer"],
                    "question": d["Question"],
                    "category": d["Category"],
                }

                self.client.batch.add_data_object(properties, "Question")

    def query(self, query_text: str):
        near_text = {"concepts": [query_text]}

        return (
            self.client.query
            .get("Question", ["question", "answer", "category"])
            .with_near_text(near_text)
            .with_limit(5)
            .do()
        )


class CallWeaviatePipelineStep(PipelineStep):

    def __init__(self, name: str):
        super().__init__(name)
        self.weaviate_client=WeaviateClient()

    def execute_step(self, input_data):
        query_text = input_data["search_text"]
        weaviate_log.info(f"Execute the query for search text {query_text}")

        response = self.weaviate_client.query(query_text=query_text)
        output_data = deepcopy(input_data)
        output_data["result_items"] = response["data"]["Get"]["Question"]
        return output_data
