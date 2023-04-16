import os
import search
import logging

from logging import config
from log_config import logging_config
from dotenv import load_dotenv

from search import SearchRequest

load_dotenv()  # take environment variables from .env.

auth = (os.getenv('OS_USERNAME'), os.getenv('OS_PASSWORD'))

config.dictConfig(logging_config)

run_logging = logging.getLogger("runner")


if __name__ == '__main__':
    search.execute_query(SearchRequest(search_text="blue dress", explain=True))
