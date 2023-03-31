import os
import sys
import unittest
import pandas as pd


PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(
    PROJECT_PATH, "../"
)
sys.path.append(SOURCE_PATH)

from pipeline import products_dagster


class TestProductsDagster(unittest.TestCase):

    def test_transform_clicks(self):
        data = [['1', "Red T-shirt", "A comfortable and stylish red t-shirt made of cotton", 15.99, "T-shirts","Red","2022-01-01"],
                ['23', "Blue Dress", "A beautiful blue dress with floral pattern and chiffon fabric", 49.99, "Dresses","Blue","2022-01-02"]]
        df = pd.DataFrame(data, columns=["id", "name", "description", "price", "category", "color", "create_date"])
        products_dagster.transform_clicks(df)


if __name__ == '__main__':
    unittest.main()
