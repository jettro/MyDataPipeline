import os

from search.template import create_update_template
from search.opensearch import opensearch

# test the connection
if opensearch.ping():
    print('Connected to Elasticsearch')
else:
    print('Could not connect to Elasticsearch')

__all__ = [
    'create_update_template'
]
