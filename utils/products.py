from fake_useragent import UserAgent
import multiprocessing
import pandas as pd
import requests
import json

from utils.catalog import Catalog


class Product(Catalog):

    __main_catalog = 'https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json'

    def __init__(self, url: str) -> None:
        self.url = url


    @staticmethod
    def get_brand_id(url):
        url = 'https://static.wbstatic.net/data'+url.split('www.wildberries.ru')[-1]+'.json'
        response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})
        return int(json.loads(response.text)['id'])
    

    def number_of_items(self, page: int, n_proc: int):
        if page % n_proc != 0:
            limit = page//n_proc + 1
            pages = (page//n_proc + 1) * n_proc
        else:
            limit = page//n_proc

        pages = [x for x in range(1, (page//n_proc + 1) * n_proc+1)]

        return limit, pages


    def get_slice_of_brand_products(self, pages: list, send_end, url: str) -> None:
    
        brandsID = self.get_brand_id(self.url)
        df = pd.DataFrame(columns = ['id', 'name', 'brand', 'brandId', 'priceU', 'salePriceU', 'logisticsCost', 'rating', 'feedbacks', 'supplierId'])

        for x in pages:
            url = f'https://catalog.wb.ru/brands/{brandsID}/catalog?appType=1&brand={brandsID}&curr=rub&dest=31&regions=80,4,68,69,30,86,40,1,66,48,111&sort=popular&page={x}'

            response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

            try:
                data = json.loads(response.text)['data']['products']
                for x in data:
                    df = pd.concat([df, pd.DataFrame([x])])
                
            except json.decoder.JSONDecodeError:
                pass

        df[['priceU', 'salePriceU', 'logisticsCost']] = df[['priceU', 'salePriceU', 'logisticsCost']] / 100
        send_end.send(df)


    def get_slice_of_catalog_products(self, pie: pd.DataFrame, pages: list, send_end, url: str) -> None:

        df = pd.DataFrame(columns = ['id', 'name', 'brand', 'brandId', 'priceU', 'salePriceU', 'logisticsCost', 'rating', 'feedbacks', 'supplierId'])

        for x in pages:
            url = f'''https://catalog.wb.ru/catalog/{pie.shard.values[0]}/catalog?appType=1&{pie['query'].values[0]}&curr=rub&dest=31&regions=80,4,68,69,30,86,40,1,66,48,111&sort=popular&page={x}'''

            response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

            try:
                data = json.loads(response.text)['data']['products']
                for x in data:
                    df = pd.concat([df, pd.DataFrame([x])])
                
            except json.decoder.JSONDecodeError:
                pass

        df[['priceU', 'salePriceU', 'logisticsCost']] = df[['priceU', 'salePriceU', 'logisticsCost']] / 100
        send_end.send(df)


    def get_slice_of_purchased_products(self, products: list, send_end, url: str=None) -> None:
        x = ','.join(list(map(str, products)))
        url = f'https://product-order-qnt.wildberries.ru/by-nm/?nm={x}'
        response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})
        
        send_end.send(pd.DataFrame(json.loads(response.text)))


    def get_slice_of_other_sellers(self, products: list, send_end, url: str=None) -> pd.DataFrame:
        df = pd.DataFrame([])
        for x in products:
            
            url = f'https://identical-products.wildberries.ru/api/v1/identical?nmID={x}'
            response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

            res = json.loads(response.text)
            df = pd.concat([df,  pd.DataFrame([{'id': x}]).merge(pd.DataFrame({'brother': res}), how='cross')])
        send_end.send(df)


    def get_sellers_name(self, sellersID: list, send_end, url: str=None) -> pd.DataFrame:
        df = pd.DataFrame([])
        for x in sellersID:
            
            url = f'https://www.wildberries.ru/webapi/seller/data/short/{str(x)}'
            response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

            res = json.loads(response.text)
            df = pd.concat([df,  pd.DataFrame([res])])
        send_end.send(df)


    def create_loop(self, target, limit: int, data: list, n_proc: int, added_data: pd.DataFrame=None) -> list:
        jobs, pipe_list = [], []
        if added_data is None:
            for i in range(n_proc):
                        recv_end, send_end = multiprocessing.Pipe(True)
                        process = multiprocessing.Process(target=target, args=(data[limit*i:limit*(i+1)], send_end, self.url))
                        jobs.append(process)
                        pipe_list.append(recv_end)
                        process.start()
        else: 
            for i in range(n_proc):
                        recv_end, send_end = multiprocessing.Pipe(True)
                        process = multiprocessing.Process(target=target, args=(added_data, data[limit*i:limit*(i+1)], send_end, self.url))
                        jobs.append(process)
                        pipe_list.append(recv_end)
                        process.start()
        return pipe_list


    def multiprocess(self, var, mode: str=None) -> pd.DataFrame:
        n_proc = multiprocessing.cpu_count()

        if isinstance(var, int):
            if 'brands' in self.url:
                limit, pages = self.number_of_items(var, n_proc)
                pipe_list = self.create_loop(self.get_slice_of_brand_products, limit, pages, n_proc)

            elif 'catalog' in self.url:

                pie = self.get_catalog(url=self.__main_catalog)
                pie = pie.query(f'''url == "{self.url.split('www.wildberries.ru')[-1]}"''')

                limit, pages = self.number_of_items(var, n_proc)
                pipe_list = self.create_loop(self.get_slice_of_catalog_products, limit, pages, n_proc, pie)
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

            return df

        elif isinstance(var, pd.DataFrame):
            limit, pages = self.number_of_items(var.shape[0], n_proc)

            if mode == 'other_sellers':
                pipe_list = self.create_loop(self.get_slice_of_other_sellers, limit, list(var.id), n_proc)
            elif mode == 'purchased_products':
                pipe_list = self.create_loop(self.get_slice_of_purchased_products, limit, list(var.id), n_proc)
            else:
                print('Mode is not mean')
                return pd.DataFrame([])

            return pd.concat([x.recv() for x in pipe_list])
