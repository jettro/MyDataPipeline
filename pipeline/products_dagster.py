import json
import re

import pandas as pd

from dagster import MetadataValue, Output, asset

from search import create_update_template
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
def transform_sales(products: pd.DataFrame):
    """Load the sold items from the csv file
    """
    sales = pd.read_csv('./data_sources/sales.csv')

    merged_products = pd.merge(products, sales, left_on="id", right_on="product_id")
    merged_products = merged_products.drop(columns=['product_id'])

    metadata = {
        "transformation": "Read the sales from a csv file and added the amount of sales to the product",
        "preview": MetadataValue.md(merged_products[["id", "name", "description", "price", "category", "color",
                                                     "create_date", "sold_items"]]
                                    .to_markdown()),
    }

    return Output(value=merged_products, metadata=metadata)


@asset
def transform_stock(transform_sales: pd.DataFrame):
    """Load the stock items from the csv file
    """
    stocks = pd.read_csv('./data_sources/stock.csv')

    merged_products = pd.merge(transform_sales, stocks, left_on="id", right_on="product_id")
    merged_products = merged_products.drop(columns=['product_id'])

    metadata = {
        "transformation": "Read the clicks from an external system and added the amount of clicks to the product",
        "preview": MetadataValue.md(merged_products[["id", "name", "description", "price", "category", "color",
                                                     "create_date", "sold_items", "stock_amount"]]
                                    .to_markdown()),
    }

    return Output(value=merged_products, metadata=metadata)


@asset
def transform_clicks(transform_stock: pd.DataFrame):
    """Load the clicks from external system and add the clicks to the products
    """
    clicks = _load_json_lines_from_file('./data_sources/clicks.jsonl')
    transform_stock["num_clicks"] = transform_stock["id"].map(lambda x: clicks.get(str(x))["clicks"])

    metadata = {
        "transformation": "Read the clicks from an external system and added the amount of clicks to the product",
        "preview": MetadataValue.md(transform_stock[["id", "name", "description", "price", "category", "color",
                                                     "create_date", "sold_items", "stock_amount", "num_clicks"]]
                                    .to_markdown()),
    }
    return Output(value=transform_stock, metadata=metadata)


@asset
def load(transform_clicks: pd.DataFrame):
    """Load the product data into OpenSearch
    """
    create_update_template()
    products_index = create_index()

    # iterate over all DataFrame items and send them to Opensearch

    for index, row in transform_clicks.iterrows():
        product = row.to_dict()
        index_product(product=product, index_name=products_index)

    switch_alias_to(products_index)

    metadata = {
        "preview": MetadataValue.md(
            "Created the index " + products_index + " with " + str(len(transform_clicks)) + " products")
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
