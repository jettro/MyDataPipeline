"""
This runner uses langchain to index content from the Dutch Rijksoverheid about Vraag Antwoord Combinaties. The project
uses langchain to send the data to OpenSearch as well as Weaviate. Results can be compared, but for me the needed
code for both solutions is more important at the moment.
"""
import logging
import os
from logging import config

from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Weaviate, VectorStore, OpenSearchVectorSearch

from langchainmod import CustomXMLLoader
from log_config import logging_config
from search import OpenSearchClient
from weaviatedb import WeaviateClient

WEAVIATE_CLASS = "RijksoverheidVac"
OPENSEARCH_INDEX = "rijksoverheid-vac"

load_dotenv()  # take environment variables from .env.
config.dictConfig(logging_config)  # Load the logging configuration
run_logging = logging.getLogger("runner")  # initialize the main logger


def load_weaviate_schema(weaviate_client: WeaviateClient) -> None:
    run_logging.info(f"(Re)Load the Weaviate schema class: {WEAVIATE_CLASS}")
    if weaviate_client.does_class_exist(WEAVIATE_CLASS):
        weaviate_client.delete_class(WEAVIATE_CLASS)
        run_logging.info("Removed the existing Weaviate schema.")

    weaviate_client.create_classes("./config_files/rovac_weaviate_schema.json")
    run_logging.info("New schema for langchain rijksoverheid vac loaded.")


def load_content(vector_store: VectorStore) -> None:
    run_logging.info("Load the content")

    custom_xml_loader = CustomXMLLoader(file_path="https://opendata.rijksoverheid.nl/v1/infotypes/faq?rows=200")
    docs = custom_xml_loader.load()

    run_logging.info("Store the content")
    vector_store.add_documents(docs)


def run_weaviate(query: str = "enter your query", do_load_content: bool = False) -> None:
    weaviate_client = WeaviateClient()
    vector_store = Weaviate(
        client=weaviate_client.client,
        index_name=WEAVIATE_CLASS,
        text_key="text"
    )

    if do_load_content:
        load_weaviate_schema(weaviate_client=weaviate_client)
        load_content(vector_store=vector_store)

    index = VectorStoreIndexWrapper(vectorstore=vector_store)
    docs = index.vectorstore.similarity_search(
        query=query,
        search_distance=0.6,
        additional=["certainty"])

    print(f"\nResults from: Weaviate")
    for doc in docs:
        print(f"{doc.metadata['_additional']['certainty']} - {doc.page_content}")


def run_opensearch(query: str = "enter your query", do_load_content: bool = False) -> None:
    auth = (os.getenv('OS_USERNAME'), os.getenv('OS_PASSWORD'))
    opensearch_client = OpenSearchClient()

    vector_store = OpenSearchVectorSearch(
        index_name=OPENSEARCH_INDEX,
        embedding_function=OpenAIEmbeddings(openai_api_key=os.getenv('OPEN_AI_API_KEY')),
        opensearch_url="https://localhost:9200",
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
        http_auth=auth
    )

    if do_load_content:
        opensearch_client.delete_index(OPENSEARCH_INDEX)
        load_content(vector_store=vector_store)

    docs = vector_store.similarity_search_with_score(query=query)
    print(f"\nResults from: OpenSearch")
    for doc, _score in docs:
        print(f"{_score} - {doc.page_content}")


if __name__ == '__main__':
    run_logging.info("Starting the script Langchain Rijksoverheid Vraag Antwoord Combinaties")

    run_weaviate(query="waar moet ik bij een vrachtwagen op letten",
                 do_load_content=False)

    run_opensearch(query="waar moet ik bij een vrachtwagen op letten",
                   do_load_content=True)