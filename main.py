import pandas as pd
import datetime as dt
import time

from utils.products import Product
from utils.catalog import Catalog
from db.database import create


if __name__ == '__main__':

    create()

    #url = 'https://www.wildberries.ru/catalog/igrushki/antistress'
    url = 'https://www.wildberries.ru/brands/prosveshchenie'

    products = Product(url)

    # product = products.multiprocess(20)

    # product.to_excel('product.xlsx', index=False)

    s = time.time()
    df = products.multiprocess(pd.DataFrame([{'id': 67824893}, {'id': 163990051}, {'id':  28918982}]), mode='other_sellers', recollection_=True, avaliable=False)
    e = time.time()
    print(e-s, df.shape)

    df.to_excel('test.xlsx', index=False)

    # catalog = Catalog() 26191563
    # catalog.ge_catalog().to_excel('test.xlsx', index=False)
