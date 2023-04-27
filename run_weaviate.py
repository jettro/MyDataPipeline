import json

from weaviatedb import weaviate_client

if __name__ == '__main__':
    # weaviate.create_classes()
    print(weaviate.get_schema())
    # weaviate.load_data()
    print(json.dumps(weaviate.query(), indent=4))
