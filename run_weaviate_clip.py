import os
import base64

import streamlit as st

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


def query(client: WeaviateClient, query_text: str, the_limit: int = 3):
    near_text = {"concepts": [query_text]}

    return (
        client.client.query
        .get(WEAVIATE_CLASS, ["filename"])
        .with_near_text(near_text)
        .with_limit(the_limit)
        .with_additional(properties=["certainty", "distance"])
        .do()
    )


def reload_data(client: WeaviateClient):
    load_weaviate_schema(client=client, schema_path="./config_files/weaviate_clip.json")
    store_images(client)


if __name__ == '__main__':
    weaviate_client = WeaviateClient(overrule_weaviate_url="http://localhost:8080")
    st.title("Search for toys")

    st.sidebar.button(label="Reload data",
                      key="reload_data",
                      on_click=reload_data,
                      kwargs={"client": weaviate_client})

    n_cols = 3
    n_picts = 6
    n_rows = int(1 + n_picts // n_cols)
    the_query = st.text_input('describe toy in one or a few words')
    rows = [st.columns(n_cols) for _ in range(n_rows)]
    cols = [column for row in rows for column in row]
    if the_query:
        response = query(client=weaviate_client, query_text=the_query, the_limit=n_picts)
        if response["data"]["Get"]["Toys"]:
            picts = response["data"]["Get"]["Toys"]
            for col, pict in zip(cols, picts):
                filename = pict["filename"]
                certainty = pict["_additional"]["certainty"]
                with col.container():
                    col.image(image="./data_sources/images/" + filename,
                              caption=filename,
                              width=200)
                    col.write(f"certainty: {'{:.5f}'.format(certainty)}")
