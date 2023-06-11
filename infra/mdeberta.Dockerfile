FROM semitechnologies/qna-transformers:custom
RUN MODEL_NAME=timpal0l/mdeberta-v3-base-squad2 ./download.py