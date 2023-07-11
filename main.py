import pandas as pd
import datetime as dt
import time

from utils.products import Product
from utils.catalog import Catalog
from db.database import create


if __name__ == '__main__':

    print()
    print()

    create()

    pages = 10
    #url = 'https://www.wildberries.ru/catalog/igrushki/antistress'
    url = 'https://www.wildberries.ru/catalog/dlya-doma/hozyaystvennye-tovary/stirka?sort=popular&xsubject=1080'

    products = Product(url)

    s = time.time()
    product = products.multiprocess(pages)
    e = time.time()
    print('Количество просматриваемых страниц: ', pages)
    print('Количество карточек: ', product.shape[0])
    print('Время сбора всех карточек: ', e-s) 
    
    product.to_excel('products.xlsx', index=False)
    
    # print()
    # print()

    # s = time.time()
    # df = products.multiprocess(product, mode='other_sellers', recollection_= False, avaliable=True)
    # e = time.time()

    # print('Количество контрагентов: ', df.shape[0])
    # print(f'Время сбора всех контрагентов к количеству карточек равному {product.shape[0]}: ', e-s) 

    # df.to_excel('counterparty.xlsx', index=False)

    
    # print()
    # print()
