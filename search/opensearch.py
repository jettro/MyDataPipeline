import os
import logging

from opensearchpy import OpenSearch
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()  # take environment variables from .env.
auth = (os.getenv('OS_USERNAME'), os.getenv('OS_PASSWORD'))

search_log = logging.getLogger("search")

ALIAS_NAME = "products"

# create an Elasticsearch instance
opensearch = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    http_auth=auth)


def create_index():
    """
    Create a new index. Name of the index is a combination of the configured ALIAS_NAME and a time stamp in the format
    of YearMonthDayHourMinuteSecond. Before the index is created, we remove it if it already exists. The settings
    and mappings are obtained from the shoes_index.json in the config folder.
    :return: The name of the created index
    """
    index_name = f'{ALIAS_NAME}-{datetime.now().strftime("%Y%m%d%H%M%S")}'

    opensearch.indices.delete(index=index_name, ignore_unavailable=True)
    opensearch.indices.create(index=index_name)

    search_log.info(f'Created a new index with the name {index_name}')
    return index_name


def switch_alias_to(index_name):
    """
    Checks if the alias as configured is already available, if so, remove all indexes it points to. When finished add
    the provided index to the alias.
    :param index_name: Name of the index to assign to the alias
    :return:
    """
    search_log.info(f'Assign alias {ALIAS_NAME} to {index_name}')
    body = {
        "actions": [
            {"remove": {"index": f'{ALIAS_NAME}-*', "alias": ALIAS_NAME}},
            {"add": {"index": index_name, "alias": ALIAS_NAME}}
        ]
    }
    opensearch.indices.update_aliases(body=body)


def index_product(product, index_name):
    """
    Send the provided shoe to Elasticsearch to index that shoe into the provided index.
    :param product: The Product to index
    :param index_name: The index to use for indexing the shoe
    :return:
    """
    search_log.info(f'Indexing shoe: {product["id"]} into index with name {index_name}')
    opensearch.index(index=index_name, id=product["id"], body=product)
