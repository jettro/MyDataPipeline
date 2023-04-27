import os

from search.product_search import execute_query, SearchRequest
from search.template import create_update_template
from search.opensearch import opensearch
from search.query_pipeline import QueryPipeline, PipelineStep, LogInputPipelineStep
from search.reorder_query_pipeline_step import ReorderQueryPipelineStep

# test the connection
if opensearch.ping():
    print('Connected to Elasticsearch')
else:
    print('Could not connect to Elasticsearch')

__all__ = [
    'create_update_template',
    'execute_query',
    'SearchRequest',
    'QueryPipeline',
    'PipelineStep',
    'LogInputPipelineStep',
    'ReorderQueryPipelineStep'
]
