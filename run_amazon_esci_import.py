import json

import pandas as pd
import os

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

LOCAL_ESCI_PATH = os.getenv('LOCAL_ESCI_PATH')
LOCAL_ESCIS_PATH = os.getenv('LOCAL_ESCIS_PATH')


def generate_actions_from_file(file_name):
    """
    Use the file to load shoes line by line and send return them
    :param file_name: Name of the file to read
    :return: The read shoes one by one
    """
    items = []
    with open(file_name, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data['type'] == 'product' and len(data['price']) > 0:
                items.append(data)
    return items


if __name__ == '__main__':
    # df_examples = pd.read_parquet(f'{LOCAL_ESCI_PATH}/shopping_queries_dataset_examples.parquet')
    df_products = pd.read_parquet(f'{LOCAL_ESCI_PATH}/shopping_queries_dataset_products.parquet')
    # df_sources = pd.read_csv(f'{LOCAL_ESCI_PATH}/shopping_queries_dataset_sources.csv')

    # print(df_examples.columns)
    # print(df_products.columns)
    products_en = generate_actions_from_file(f'{LOCAL_ESCIS_PATH}/sample.json')
    print(json.dumps(products_en[1], indent=2))
    print(len(products_en))

    asin_ = df_products.loc[df_products['product_id'] == products_en[1]['asin']]
    print(asin_)
    print(asin_.loc[211730].to_json())
