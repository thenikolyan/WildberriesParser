from fake_useragent import UserAgent
import pandas as pd
import requests
import json


class Catalog:
    def __init__(self, url: str) -> None:
        self.url = url


    def get_json_catalog(self, url: str=None) -> list:
        if url is None:
            url = self.url

        response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})
        return (json.loads(response.text))


    def get_table_catalog(self, data: list=None, url: str=None, result: pd.DataFrame=pd.DataFrame([])) -> pd.DataFrame:
        
        if url is None:
            url = self.url

        if data is None:
            data = self.get_json_catalog(url)

        for x in data:
            if x.get('childs') is not None:
                result = self.get_table_catalog(x.get('childs'), url, result)
            else:
                result = pd.concat([result, pd.DataFrame([x])])
        return result
