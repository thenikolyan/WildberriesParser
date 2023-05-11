import pandas as pd

from utils.products import Product
from utils.catalog import Catalog


if __name__ == '__main__':
    url = 'https://www.wildberries.ru/catalog/igrushki/antistress'
    #url = 'https://www.wildberries.ru/brands/prosveshchenie'

    products = Product(url)
    product = products.multiprocess(5)
    df = products.multiprocess(product, mode='other_sellers')
    df.to_excel('test.xlsx', index=False)