import json

from weaviatedb import WeaviateClient

if __name__ == '__main__':
    weaviate_client = WeaviateClient()
    # weaviate_client.delete_class("Product")
    # weaviate_client.create_classes("./config_files/product_schema.json")
    print(json.dumps(weaviate_client.get_schema(), indent=4))
    # weaviate_client.load_data()
    print(json.dumps(weaviate_client.query("high heal"), indent=4))
