# Introduction
Welcome to my data pipeline project. This is not one project, it contains multiple things that help me explore
new technologies. I'll explain the different applications below. In general the structure follows the following 
foundation.

- config_files : Contains the files need to configer components like indexes in OpenSearch or a schema in Weaviate
- data_sources : contain the different available data files used in the applications
- tests : Contain very little unit tests, only used to test small specific things to try out.
- infra : docker files to startup specific components (OpenSearch for instance)

The other folders are modules:
- pipeline : Contains the Dagster pipeline that manages the indexes in OpenSearch
- reranking : Components that can re-rank results
- search : Contains the files related to using OpenSearch for templates, data, query and a tool to parse explain output
- util : Small utilities that we can re-use in the modules
- weaviatedb : Files used to interact with Weaviate
- langchainmod : Files used to interact with Langchain code

Files
- log_config.py : Configuration for the Python logging framework
- requirements.txt : The Python libraries used in the project
- run_query_pipeline.py : runner for the Weaviate pipeline to query Weaviate using the re-ranker as well
- run_langchain_ro_vac.py : Runner for the langchain sample that imports and queries multiple vector stores

# Docker issues with Opensearch

Create the following file:
/Users/jettrocoenradie/Library/Application Support/rancher-desktop/lima/_config/override.yaml

```yaml
provision:
- mode: system
  script: |
    #!/bin/sh
    set -o xtrace
    sysctl -w vm.max_map_count=262144
    cat <<'EOF' > /etc/security/limits.d/rancher-desktop.conf
    * soft     nofile         82920
    * hard     nofile         82920
    EOF
```

You can test using curl, for now we do not check the certificate:
```bash
curl https://localhost:9200 -ku admin:admin
```

# Dagster

I am experimenting with Dagster

```
dagster dev -f ./pipeline/products_dagster.py
```

https://docs.dagster.io/getting-started

# Weaviate custom QnA module

First we need to create the custom DockerFile. Then start docker compose with the added local docker image
```shell
docker build -f mdeberta.Dockerfile -t mdeberta-qna-transformers .
docker compose -f docker-compose-weaviate.yml up -d
```
I am experimenting with streamlid to work with a gui as well. You have to run the sample with the following command:
```shell
streamlit run run_weaviate_qna.py
```


# References
Just some articles I used

## Setting up Docker/Opensearch
https://opster.com/guides/opensearch/opensearch-basics/spin-up-opensearch-cluster-with-docker/
