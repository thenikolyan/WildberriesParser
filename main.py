import pandas as pd

from utils.products import Product
from utils.catalog import Catalog


if __name__ == '__main__':
    # url = 'https://www.wildberries.ru/catalog/igrushki/antistress'
    # #url = 'https://www.wildberries.ru/brands/prosveshchenie'

    # products = Product(url)
    # product = products.multiprocess(1)
    # # product.to_excel('product.xlsx', index=False)
    # df = products.multiprocess(product, mode='purchased_products')
    # df.to_excel('test.xlsx', index=False)

    catalog = Catalog()
    catalog.ge_catalog().to_excel('test.xlsx', index=False)