import logging
from logging import config

from dotenv import load_dotenv

from log_config import logging_config
from weaviatedb import WeaviateClient

WEAVIATE_CLASS = "RijksoverheidVac"
OPENSEARCH_INDEX = "rijksoverheid-vac"

load_dotenv()  # take environment variables from .env.
config.dictConfig(logging_config)  # Load the logging configuration
run_logging = logging.getLogger("runner")  # initialize the main logger


if __name__ == '__main__':
    weaviate_client = WeaviateClient()

    weaviate_client.inspect()
