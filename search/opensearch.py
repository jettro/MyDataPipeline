import os

from opensearchpy import OpenSearch
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
auth = (os.getenv('OS_USERNAME'), os.getenv('OS_PASSWORD'))


# create an Elasticsearch instance
opensearch = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    use_ssl=True,
    verify_certs=False,
    ssl_show_warn=False,
    http_auth=auth)
