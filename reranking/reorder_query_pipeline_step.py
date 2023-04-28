import logging
from copy import deepcopy

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from util import PipelineStep

reorder_pipeline_log = logging.getLogger("reorder")

# Load the pre-trained cross-encoder model and tokenizer
model_name = "sentence-transformers/paraphrase-xlm-r-multilingual-v1"


class ReorderQueryPipelineStep(PipelineStep):

    def __init__(self, name: str):
        super().__init__(name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

    def execute_step(self, input_data):

        # Define the query and candidate results
        query = input_data["search_text"]
        results = input_data["result_items"]

        # Encode the query and candidate results together as a single input sequence
        input_ids = []
        for result in results:
            input_ids.append(
                self.tokenizer.encode(query, result['answer'], truncation=True, padding=True, return_tensors="pt"))
        input_ids = torch.cat(input_ids, dim=0)

        # Compute the similarity score between the query and each candidate result
        outputs = self.model(input_ids)
        similarity_scores = torch.softmax(outputs.logits, dim=1)[:, 1].tolist()

        # Sort the candidate results based on their similarity score
        result_scores = list(zip(results, similarity_scores))
        result_scores = sorted(result_scores, key=lambda x: x[1], reverse=True)

        output_data = deepcopy(input_data)
        output_data["result_items_reordered"] = result_scores
        return output_data

