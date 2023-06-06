import unittest

from langchainmod import AntwoordXMLLoader


class TestAntwoordXmlLoader(unittest.TestCase):

    def test_load_url(self):
        url = "https://opendata.rijksoverheid.nl/v1/infotypes/faq/45c582ea-ace6-41a5-b8ef-d8030e48d347"
        loader = AntwoordXMLLoader(file_path=url, encoding='utf-8')
        docs = loader.load()

        self.assertEqual(1, len(docs))
        print(docs[0].page_content)
