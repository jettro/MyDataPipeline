import os
import base64

from weaviatedb import WeaviateClient

WEAVIATE_CLASS = "Toys"


def load_weaviate_schema(client: WeaviateClient, schema_path: str) -> None:
    if client.does_class_exist(WEAVIATE_CLASS):
        client.delete_class(WEAVIATE_CLASS)
        print("Removed the existing Weaviate schema.")

    client.create_classes(path_to_schema=schema_path)
    print("New schema loaded.")


def store_images(client: WeaviateClient) -> None:
    with client.client.batch() as batch:
        for x in os.listdir("./data_sources/images/"):
            if x.endswith(".jpg"):
                with open("./data_sources/images/" + x, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read())
                    print(b64_string)

                data_obj = {
                    "filename": x,
                    "image": b64_string.decode('utf-8')
                }
                batch.add_data_object(
                    data_obj,
                    WEAVIATE_CLASS
                )


def query(client: WeaviateClient, query_text: str):
    near_text = {"concepts": [query_text]}

    return (
        client.client.query
        .get(WEAVIATE_CLASS, ["filename"])
        .with_near_text(near_text)
        .with_limit(5)
        .do()
    )


if __name__ == '__main__':
    weaviate_client = WeaviateClient(overrule_weaviate_url="http://localhost:8080")

    # load_weaviate_schema(client=weaviate_client, schema_path="./config_files/weaviate_clip.json")
    # store_images(weaviate_client)
    print(query(weaviate_client, "traktor"))
