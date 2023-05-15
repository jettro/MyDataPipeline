import json

from reranking import RerankCrossencoderPipelineStep, RerankOpenaiPipelineStep
from util import LogInputPipelineStep, SimplePipeline


def compare_results(response):
    results = response["result_items"]
    result_items_reranked = response["result_items_reranked_cross"]

    for r in results:
        print(f"id: {r['id']}, name {r['name'].ljust(35)}")

    print("\nRe-ranked")
    for rr in result_items_reranked:
        print(f"id: {rr['input']['id']}, score {rr['score']}, name {rr['input']['name'].ljust(35)}")


if __name__ == '__main__':
    sentences = [
        {
            "id": 1,
            "name": "This yellow dress is perfect for a cold afternoon when the sun is going down and the sky turns "
                    "red."
        },
        {
            "id": 2,
            "name": "This red dress is perfect for a special festive occasion like a wedding on the beach"
        },
        {
            "id": 3,
            "name": "A red shirt that goes perfect with any jeans or skirt"
        },
        {
            "id": 4,
            "name": "A red wedding dress for a bride that wants something different"
        }
    ]

    steps = [
        LogInputPipelineStep(name="Log the name step"),
        RerankCrossencoderPipelineStep(name="Rerank using cross encoder"),
        RerankOpenaiPipelineStep(name="Rerank using open ai")
    ]
    pipeline = SimplePipeline(steps=steps)
    response = pipeline.start_process(
        input_data={
            "search_text": "I am attending a wedding and I am looking for something to wear. I am not the bride. "
                           "I prefer to wear a red dress if possible",
            "result_items": sentences
        }
    )
    print(json.dumps(response, indent=4, default=float))
    # compare_results(response)
