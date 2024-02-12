import logging
import os
import base64

from logging import config
from dotenv import load_dotenv
from log_config import logging_config
import streamlit as st
from weaviatedb import WeaviateClient

load_dotenv()  # take environment variables from .env.
config.dictConfig(logging_config)  # Load the logging configuration

WEAVIATE_CONFIG = [
    {
        'class_name':'Toys',
        'model': 'weaviate_clip'
    },
    {
        'class_name':'Stuff',
        'model': 'weaviate_neural'
    },
]

CLASSES_PATH = './config_files/'
IMG_PATH = "./data_sources/images/"

run_logging = logging.getLogger("runner")  # initialize the main logger


def load_weaviate_schema(client: WeaviateClient, schema_path: str, weaviate_class: str) -> None:
    """
    Creates the schema in Weaviate for the configured class. The schema is removed first if it already exists.
    """
    if client.does_class_exist(weaviate_class):
        client.delete_class(weaviate_class)
        run_logging.info("Removed the existing Weaviate schema.")

    client.create_classes(path_to_schema=schema_path)
    run_logging.info("New schema loaded for class '%s'.", weaviate_class)


def store_images(client: WeaviateClient, weaviate_class:str) -> None:
    """
    Reads all jpg files from the configured img path. Each file is converted into a base64 encoded string. Next it
    is stored into Weaviate using the batch interface.

    :param client: Client for interacting with Weaviate
    :return: Nothing
    """
    with client.client.batch(batch_size=5) as batch:
        for file_name in os.listdir(IMG_PATH):
            if file_name.endswith(".jpg"):
                with open(IMG_PATH + file_name, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read())

                data_obj = {"filename": file_name, "image": b64_string.decode('utf-8')}
                batch.add_data_object(data_obj, weaviate_class)
                run_logging.info("Stored file: %s", file_name)


def query_text_images(client: WeaviateClient, query_text: str, weaviate_class:str,  the_limit: int = 3):
    """
    Queries weaviate for available images that match the provided search terms.
    :param client: Client for interacting with Weaviate
    :param query_text: Provided text for matching similar images
    :param the_limit: Number of images to return, defaults to 3
    :return: List of objects with properties filename and certainty
    """
    run_logging.info("Executing the query '%s'", query_text)
    near_text = {"concepts": [query_text]}

    response = (client.client.query
                   .get(weaviate_class, ["filename"])
                   .with_near_text(near_text)
                   .with_limit(the_limit)
                   .with_additional(properties=["certainty", "distance"])
                   .do())
    if response["data"]["Get"][weaviate_class]:
        found_picts = response["data"]["Get"][weaviate_class]
        return [{"filename": pict["filename"], "certainty": pict["_additional"]["certainty"]} for pict in found_picts]

    return []

def query_similar_images(client: WeaviateClient, query_text: str, weaviate_class:str, the_limit: int = 3):
    """
    Queries weaviate for available images that match the provided search terms.
    :param client: Client for interacting with Weaviate
    :param query_text: Provided image for matching similar images
    :param the_limit: Number of images to return, defaults to 3
    :return: List of objects with properties filename and certainty
    """
    run_logging.info("Executing the query '%s'", query_text)
    sourceImage = { "image": query_text}
    response = (client.client.query
                   .get(weaviate_class, ["filename"])
                   .with_near_image(sourceImage, encode=False)
                   .with_limit(the_limit)
                   .with_additional(properties=["certainty", "distance"])
                   .do())
    if response["data"]["Get"][weaviate_class]:
        found_picts = response["data"]["Get"][weaviate_class]
        return [{"filename": pict["filename"], "certainty": pict["_additional"]["certainty"]} for pict in found_picts]

    return []

def reload_data(client: WeaviateClient) -> None:
    """
    Loads a fresh instance of the Toys schema, removes the old one if present.
    :param client: Client for interacting with Weaviate
    :return: Nothing
    """
    for config in WEAVIATE_CONFIG:
        print(f'''{CLASSES_PATH}{config["model"]}.json''')
        load_weaviate_schema(client=client, schema_path=f'''{CLASSES_PATH}{config["model"]}.json''',weaviate_class=config['class_name'])
        store_images(client, config['class_name'])
    
    
    

def print_results(cols, picts):
    for col, picture in zip(cols, picts):
        filename = picture["filename"]
        certainty = picture["certainty"]
        with col.container():
            col.image(image="./data_sources/images/" + filename,
                        caption=filename,
                        width=200)
            col.write(f"certainty: {'{:.5f}'.format(certainty)}")

@st.cache_resource
def create_weaviate_client(url: str = None):
    """
    Utility method to make it possible for Streamlit to cache the Weaviate client access.
    :param url: String containing the url for the Weaviate cluster
    :return: The created WeaviateClient instance
    """
    return WeaviateClient(overrule_weaviate_url=url)


if __name__ == '__main__':
    weaviate_client = create_weaviate_client(url="http://localhost:8080")
    st.title("Search for toys")

    st.sidebar.button(label="Reload data",
                      key="reload_data",
                      on_click=reload_data,
                      kwargs={"client": weaviate_client})

    # Initialize the table for Streamlit with a specified number of rows and the maximum number of images
    n_cols = 3
    n_picts = 6

    n_rows = int(1 + n_picts // n_cols)
    the_query = st.text_input('describe toy in one or a few words')
    uploaded_file = st.file_uploader(label='Upload file :sunglasses:', type=['png','jpg'])

    rows = [st.columns(n_cols) for _ in range(n_rows)]
    cols = [column for row in rows for column in row]

    # Execute the query if there is text in the query box
    
    if uploaded_file:
        img_str = base64.b64encode(uploaded_file.getvalue()).decode()
        picts = query_similar_images(client=weaviate_client, query_text=img_str, weaviate_class='Stuff', the_limit=n_picts)
        st.sidebar.image(image =uploaded_file.getvalue())
        print_results(cols, picts)
    
    elif the_query:
        picts = query_text_images(client=weaviate_client, query_text=the_query, weaviate_class= 'Toys', the_limit=n_picts)
        print_results(cols, picts)
    

