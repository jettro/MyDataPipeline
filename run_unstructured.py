from unstructured.partition.auto import partition
from unstructured.staging.base import elements_to_json

if __name__ == '__main__':
    elements = partition(filename="data_sources/Luminis-whitepaper-datastrategie-jan-2020.pdf")

    # elements_to_json(elements, filename="./whitepaper.json")

    for element in elements:
        print(element.to_dict().get("text"))
