from fake_useragent import UserAgent
import multiprocessing
import pandas as pd
import numpy as np
import requests
import json
import copy
import time

from utils.catalog import Catalog
from db.database import get_sellers, get_articuls, insert_seller, insert_articul, recollection

import warnings
warnings.filterwarnings('ignore')


class Product(Catalog):

    __main_catalog = 'https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json'


    def __init__(self, url: str) -> None:
        if url is None:
            self.url = ''
        else:
            self.url = url


    @staticmethod
    def get_brand_id(url) -> int:
        url = 'https://static.wbstatic.net/data'+url.split('www.wildberries.ru')[-1]+'.json'
        response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})
        return int(json.loads(response.text)['id'])
    

    def check_avaliable(self, df: pd.DataFrame, articuls: list=[], avaliable: bool=True) -> pd.DataFrame:

        if not df.empty:
            df[['priceU', 'salePriceU', 'logisticsCost']] = df[['priceU', 'salePriceU', 'logisticsCost']] / 100
        else:
            return pd.DataFrame(columns=['id', 'name', 'brand', 'brandId', 'priceU', 'salePriceU', 'logisticsCost', 'rating', 'feedbacks', 'supplierId'])

        # if card exsists, but nol avaliable
        if not avaliable:
            try:
                df = df.dropna(subset='wh')
            except KeyError:
                return pd.DataFrame(columns=['id', 'name', 'brand', 'brandId', 'priceU', 'salePriceU', 'logisticsCost', 'rating', 'feedbacks', 'supplierId'])
        
        return df[['id', 'name', 'brand', 'brandId', 'priceU', 'salePriceU', 'logisticsCost', 'rating', 'feedbacks', 'supplierId']]


    def number_of_items(self, page: int, n_proc: int):
        if page % n_proc != 0:
            limit = page//n_proc + 1
            pages = (page//n_proc + 1) * n_proc
        else:
            limit = page//n_proc

        pages = [x for x in range(1, (page//n_proc + 1) * n_proc+1)]

        return limit, pages


    def get_data_by_articuls(self, articuls: list, avaliable: bool=True):

        df = pd.DataFrame([])

        limit = 1 if len(articuls) < 100 else int(len(articuls)/100)+1

        for x in range(limit):

            tmp_articuls = ';'.join(articuls[x*100:(x+1)*100])

            url = 'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1257786&regions=80,38,4,64,83,33,68,70,69,30,86,75,40,1,66,110,22,31,48,71,114&nm=' + tmp_articuls
            response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

            df = pd.concat([df, pd.DataFrame(json.loads(response.text)['data']['products'])])

        return self.check_avaliable(df, articuls, avaliable)


    def get_slice_of_brand_products(self, pages: list, send_end, url: str, avaliable: bool=True) -> None:
    
        brandsID = self.get_brand_id(self.url)
        df = pd.DataFrame([])

        for x in pages:

            url = f'https://catalog.wb.ru/brands/{brandsID}/catalog?appType=1&brand={brandsID}&curr=rub&dest=-1257786&regions=80,38,4,64,83,33,68,70,69,30,86,75,40,1,66,110,22,31,48,71,114&sort=popular&page={x}'

            response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

            try:
                data = json.loads(response.text)['data']['products']
                for y in data:
                    df = pd.concat([df, pd.DataFrame([y])])
                
            except json.decoder.JSONDecodeError:
                pass

        send_end.send(self.check_avaliable(df, [], avaliable))


    def get_slice_of_catalog_products(self, added_data: pd.DataFrame, pages: list, send_end, url: str, avaliable: bool=True) -> None:
        

        if isinstance(added_data, list):
            pie, subcategory = added_data[0], added_data[1]
            url = f'''https://catalog.wb.ru/catalog/{pie.shard.values[0]}/catalog?appType=1&{pie['query'].values[0]}&curr=rub&dest=-1257786&regions=80,38,4,64,83,33,68,70,69,30,86,75,40,1,66,110,22,31,48,71,114&{subcategory}&'''
        else:
            url = f'''https://catalog.wb.ru/catalog/{added_data.shard.values[0]}/catalog?appType=1&{added_data['query'].values[0]}&curr=rub&dest=-1257786&regions=80,38,4,64,83,33,68,70,69,30,86,75,40,1,66,110,22,31,48,71,114&sort=popular&'''

        df = pd.DataFrame([])

        for x in pages:
            
            url += rf'''page={x}'''

            response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

            try:
                data = json.loads(response.text)['data']['products']
                for x in data:
                    df = pd.concat([df, pd.DataFrame([x])])
                
            except json.decoder.JSONDecodeError:
                pass

        send_end.send(self.check_avaliable(df, [], avaliable))


    def get_slice_of_purchased_products(self, products: list, send_end, url: str=None) -> None:
        x = ','.join(list(map(str, products)))
        url = f'https://product-order-qnt.wildberries.ru/by-nm/?nm={x}'
        response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})
        
        send_end.send(pd.DataFrame(json.loads(response.text)))


    def get_slice_of_other_sellers(self,  recollection_: bool, articul: list, send_end, url: str=None, avaliable: bool=True) -> pd.DataFrame:

        df = pd.DataFrame(columns=['id', 'brother'])
        SQLarticul = get_articuls(articul)
        unchangable_articul = copy.deepcopy(articul)
        articul = set(articul)

        if not recollection_:
            articul.difference_update(set(SQLarticul.id))


        for x in list(articul):

            if x in list(df.id):
                continue

            try:
                url = f'https://identical-products.wildberries.ru/api/v1/identical?nmID={x}'
                response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})
                res = json.loads(response.text)

                articuls = [x] + res
                df = pd.concat([df,  pd.DataFrame({'id': articuls}).merge(pd.DataFrame({'brother': articuls}), how='cross')])
            except json.decoder.JSONDecodeError as e:
                pass
                # print(4)
                # print(e)

        insert_articul(df)
        df = df.query('id != brother')

        SQLarticul = pd.concat([SQLarticul, df])
        SQLarticul = SQLarticul[SQLarticul.id.isin(list(unchangable_articul))].reset_index(drop=True)


        ids = self.get_data_by_articuls(list(set(list(SQLarticul.id.astype('int').astype('str')))), not avaliable)
        brothers = self.get_data_by_articuls(list(set(list(SQLarticul.brother.astype('int').astype('str')))), avaliable)

        tmp = [SQLarticul, ids, brothers]
        send_end.send(tmp)


    def get_sellers_name(self, sellersID: list, send_end, url: str=None, avaliable: bool=True) -> pd.DataFrame:
        sellersID = set(sellersID)
        sellers = get_sellers()

        sellersID.difference_update(set(sellers.id))
            
        df = pd.DataFrame(columns = ['id', 'name', 'fineName', 'ogrn', 'trademark', 'legalAddress', 'isUnknown'])
        for x in list(sellersID):
            
            url = f'https://www.wildberries.ru/webapi/seller/data/short/{str(x)}'
            response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

            res = json.loads(response.text)
            df = pd.concat([df,  pd.DataFrame([res])])

        df = df.replace('', np.nan).fillna(0).astype({'id': 'int', 'name': 'str', 'fineName': 'str', 'ogrn': 'int64', 'trademark': 'str', 'legalAddress': 'str', 'isUnknown': 'str'})

        insert_seller(df)

        sellers = pd.concat([sellers, df])

        send_end.send(sellers)


    def add_seller_names(self, df: pd.DataFrame, n_proc: int=4, avaliable: bool=True) -> pd.DataFrame:

        sellers = list(set(list(df.supplierId)))
        limit, pages = self.number_of_items(len(sellers), n_proc)
        sellers_pipe_list = self.create_loop(target=self.get_sellers_name, limit=limit, data=sellers, n_proc=n_proc, avaliable=avaliable)
        sellers = pd.concat([x.recv() for x in sellers_pipe_list])

        return df.merge(sellers.drop_duplicates(keep='first').rename(columns={'id': 'supplierId', 'name': 'seller_name'}), on='supplierId', how='left')


    def create_loop(self, target, limit: int, data: list, n_proc: int, avaliable: bool=True, added_data: any=None) -> list:
        jobs, pipe_list = [], []
        if added_data is None:
            for i in range(n_proc):
                        recv_end, send_end = multiprocessing.Pipe(True)
                        process = multiprocessing.Process(target=target, args=(data[limit*i:limit*(i+1)], send_end, self.url, avaliable))
                        jobs.append(process)
                        pipe_list.append(recv_end)
                        process.start()
        else:
            for i in range(n_proc):
                        recv_end, send_end = multiprocessing.Pipe(True)
                        process = multiprocessing.Process(target=target, args=(added_data, data[limit*i:limit*(i+1)], send_end, self.url, avaliable))
                        jobs.append(process)
                        pipe_list.append(recv_end)
                        process.start()
        return pipe_list


    def multiprocess(self, var, mode: str=None, recollection_: bool=False, avaliable: bool=True) -> pd.DataFrame:
        n_proc = multiprocessing.cpu_count()

        if isinstance(var, int):
            if 'brands' in self.url:
                limit, pages = self.number_of_items(var, n_proc)
                pipe_list = self.create_loop(target=self.get_slice_of_brand_products, limit=limit, data=pages, n_proc=n_proc, avaliable=avaliable)

            elif 'catalog' in self.url:
                limit, pages = self.number_of_items(var, n_proc)

                if '?' in self.url:
                    url_query, url_added = (self.url.split('www.wildberries.ru')[-1]).split('?')

                    pie = self.get_catalog(url=self.__main_catalog)
                    pie = pie.query(f'''url == "{url_query}"''')

                    pipe_list = self.create_loop(target=self.get_slice_of_catalog_products, limit=limit, data=pages, n_proc=n_proc, avaliable=avaliable, added_data=[pie, url_added])
                else:
                    pie = self.get_catalog(url=self.__main_catalog)
                    pie = pie.query(f'''url == "{self.url.split('www.wildberries.ru')[-1]}"''')

                    pipe_list = self.create_loop(target=self.get_slice_of_catalog_products, limit=limit, data=pages, n_proc=n_proc, avaliable=avaliable, added_data=pie)
                
            else:
                print('Mode is not mean')
                return pd.DataFrame([])
            
            # add seller names
            df = pd.concat([x.recv() for x in pipe_list])
            sellers = list(set(list(df.supplierId)))
            limit, pages = self.number_of_items(len(sellers), n_proc)
            sellers_pipe_list = self.create_loop(self.get_sellers_name, limit, sellers, n_proc)
            sellers = pd.concat([x.recv() for x in sellers_pipe_list])

            df = df.merge(sellers.rename(columns={'id': 'supplierId', 'name': 'seller_name'}), on='supplierId', how='left')

            return df.drop_duplicates(keep='first')

        elif isinstance(var, pd.DataFrame):
            limit, pages = self.number_of_items(var.shape[0], n_proc)

            if mode == 'other_sellers':

                pipe_list = self.create_loop(target=self.get_slice_of_other_sellers, limit=limit, data=list(var.id), n_proc=n_proc, avaliable=avaliable, added_data=recollection_)

                if recollection_:
                    recollection(flag=recollection_, table='articuls')

                listdf = [x.recv() for x in pipe_list]
                SQLarticul = pd.concat([x[0] for x in listdf]).drop_duplicates(keep='first').query('id != brother')
                ids = pd.concat([x[1] for x in listdf]).drop_duplicates(keep='first')
                brothers = pd.concat([x[2] for x in listdf]).drop_duplicates(keep='first')

                SQLarticul = SQLarticul.merge(self.add_seller_names(df=ids, n_proc=n_proc, avaliable=avaliable).drop(columns=['fineName', 'ogrn', 'trademark', 'legalAddress', 'isUnknown']), on='id', how='left')
                SQLarticul = SQLarticul.merge(self.add_seller_names(df=brothers, n_proc=n_proc, avaliable=avaliable).drop(columns=['fineName', 'ogrn', 'trademark', 'legalAddress', 'isUnknown']).rename(columns={'id': 'brother'}), on='brother', how='left', suffixes=('', '_brother'))

                SQLarticul = SQLarticul.dropna()

                return SQLarticul

            elif mode == 'purchased_products':
                pipe_list = self.create_loop(target=self.get_slice_of_purchased_products, limit=limit, data=list(var.id), n_proc=n_proc, avaliable=avaliable)
            else:
                print('Mode is not mean')
                return pd.DataFrame([])

            return pd.concat([x.recv() for x in pipe_list])
        
        else:
            print('Mode is not mean')
            return pd.DataFrame([])
