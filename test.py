import datetime as dt
import copy

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


test([28853096, 83379828, 26054112])

#print( pd.DataFrame({'id': [28853096, 83379828]}).merge(pd.DataFrame({'brother': [28853096, 83379828]}), how='cross'))