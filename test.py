import datetime as dt
import copy

from fake_useragent import UserAgent
import requests
import json

from db.database import *

create()

def test(articul: list) -> pd.DataFrame:

    df = pd.DataFrame(columns=['id', 'brother'])
    SQLarticul = get_articuls(articul)
    unchangable_articul = copy.deepcopy(articul)
    articul = set(articul)
    articul.difference_update(set(SQLarticul.id))

    for x in list(articul):

        if x in list(df.id):
            continue

        url = f'https://identical-products.wildberries.ru/api/v1/identical?nmID={x}'
        response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})
        res = json.loads(response.text)

        articuls = [x] + res
        df = pd.concat([df,  pd.DataFrame({'id': articuls}).merge(pd.DataFrame({'brother': articuls}), how='cross')])

    insert_articul(df)

    SQLarticul = pd.concat([SQLarticul, df])

    SQLarticul = SQLarticul[SQLarticul.id.isin(list(unchangable_articul))].reset_index(drop=True)

    return SQLarticul


# test([28853096, 83379828, 26054112])

print('a' in 'asd')

#print( pd.DataFrame({'id': [28853096, 83379828]}).merge(pd.DataFrame({'brother': [28853096, 83379828]}), how='cross'))

# df = pd.read_excel('SQLarticul.xlsx')
# print(df.head())
# print(df.dtypes)

# print(df.shape)

# df = df.astype('int64').drop_duplicates(subset=['id', 'brother'], keep=False)
# print(df.shape)


url = 'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=31&regions=80,4,83,68,69,30,86,40,1,66,31,48,111&spp=28&nm=' + '34560791'
response = requests.get(url, headers={'User-Agent': f'{UserAgent().random}'})

data = pd.DataFrame(json.loads(response.text)['data']['products'])

print(data)

