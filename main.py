import pandas as pd
import datetime as dt
import time

from utils.products import Product
from utils.catalog import Catalog


if __name__ == '__main__':
    #url = 'https://www.wildberries.ru/catalog/igrushki/antistress'
    url = 'https://www.wildberries.ru/brands/prosveshchenie'

    products = Product(url)

    product = products.multiprocess(20)

    product.to_excel('product.xlsx', index=False)

    s = time.time()
    df = products.multiprocess(product, mode='other_sellers')
    e = time.time()
    print(e-s, df.shape)

    df.to_excel('test.xlsx', index=False)

    # catalog = Catalog() 26191563
    # catalog.ge_catalog().to_excel('test.xlsx', index=False)

