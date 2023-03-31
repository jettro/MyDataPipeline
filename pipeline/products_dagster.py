import json
import re

import pandas as pd

from dagster import MetadataValue, Output, asset

from search.opensearch import create_index, switch_alias_to, index_product


@asset
def products():
    """Get product data from the csv file in the data_sources folder
    """
    df = pd.read_csv('./data_sources/products.csv')
    metadata = {
        "num_records": len(df),
        "preview": MetadataValue.md(df[["id", "name", "description", "price", "category", "color", "create_date"]]
                                    .to_markdown()),
    }
    
    return Output(value=df, metadata=metadata)
    

@asset
def transform_clicks(products: pd.DataFrame):
    """Load the clicks from external system and add the clicks to the products
    """
    clicks = _load_json_lines_from_file('./data_sources/clicks.jsonl')
    products["num_clicks"] = products["id"].map(lambda x: clicks.get(str(x))["clicks"])
    
    metadata = {
        "num_records": len(products),
        "transformation": "Read the clicks from an external system and added the amount of clicks to the product",
        "preview": MetadataValue.md(products[["id", "name", "description", "price", "category", "color", "create_date",
                                              "num_clicks"]].to_markdown()),
    }
    return Output(value=products, metadata=metadata)


@asset
def load(transform_clicks: pd.DataFrame):
    """Load the product data into OpenSearch
    """
    products_index = create_index()
    
    # iterate over all DataFrame items and send them to Opensearch

    for index, row in transform_clicks.iterrows():
        product = row.to_dict()
        index_product(product=product, index_name=products_index)
        
    switch_alias_to(products_index)
    
    metadata = {
        "preview": MetadataValue.md("Created the index " + products_index + " with " + str(len(transform_clicks)) + " products")
    }
    
    return Output(value=transform_clicks, metadata=metadata)
    
    
def _load_json_lines_from_file(file_name):
    """
    Use the file to load items line by line and send return them
    :param file_name: Name of the file to read
    :return: The read items one by one
    """
    items = {}
    
    input_file = open(file_name, 'r')
    for line in input_file:
        line_obj = json.loads(line)
        
        product_id = re.search(r'/(\d+)$', line_obj["url"]).group(1)
        items[product_id] = line_obj
    
    return items
