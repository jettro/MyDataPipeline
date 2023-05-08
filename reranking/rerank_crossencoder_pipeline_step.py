import logging
from copy import deepcopy

from sentence_transformers import CrossEncoder

from util import PipelineStep

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2', max_length=512,)


class RerankCrossencoderPipelineStep(PipelineStep):

    def __init__(self, name: str, enabled: bool = True):
        super().__init__(name, enabled=enabled)
        self.logger = logging.getLogger("reorder")

    def execute_step(self, input_data):
        if not self.enabled:
            self.logger.info(f"Step {self.name} is disabled.")
            return input_data

        # Define the query and candidate results
        query = input_data["search_text"]
        query_results = input_data["result_items"]

        model_inputs = [[query, result["name"]] for result in query_results]
        scores = model.predict(model_inputs, apply_softmax=True)

        # Sort the scores in decreasing order
        results = [{'input': inp, 'score': score} for inp, score in zip(query_results, scores)]
        results = sorted(results, key=lambda x: x['score'], reverse=True)

        output_data = deepcopy(input_data)
        output_data["result_items_reranked_cross"] = results
        return output_data
