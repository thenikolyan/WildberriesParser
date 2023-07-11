import sqlite3
import pandas as pd
import requests
import json

from fake_useragent import UserAgent

conn = sqlite3.connect('.\db\lemon.db')

def create() -> None:

    conn.execute('''create table if not exists sellers(
                    id int not null,
                    name text not null,
                    fineName text not null,
                    ogrn bigint not null,
                    trademark text not null,
                    legalAddress text not null default "None",
                    isUnknown bool not null
                    );''')
    
    conn.execute('''create table if not exists articuls(
                    id bigint not null,
                    brother bigint not null
                    );''')
    
    conn.commit()
    return None


def get_sellers() -> pd.DataFrame:
    cur = conn.cursor()
    cur.execute(f'select * from sellers')
    df = pd.DataFrame(cur.fetchall(), columns = ['id', 'name', 'fineName', 'ogrn', 'trademark', 'legalAddress', 'isUnknown'])
    return df


def get_articuls(articul: list) -> pd.DataFrame:
    cur = conn.cursor()
    cur.execute(f'''select * from articuls where id in ({','.join(['"'+str(x)+'"' for x in articul])})''')
    df = pd.DataFrame(cur.fetchall(), columns = ['id', 'brother'])
    return df


def insert_seller(df: pd.DataFrame) -> None:


    df['name'] = df['name'].apply(lambda x: x.replace('"', ''))
    df['fineName'] = df['fineName'].apply(lambda x: x.replace('"', ''))
    df['trademark'] = df['trademark'].apply(lambda x: x.replace('"', ''))
    df['legalAddress'] = df['legalAddress'].apply(lambda x: x.replace('"', ''))

    df = df.to_dict('records')
    for x in df: 
        conn.execute(
            f'''insert or ignore into sellers (id, name, fineName, ogrn, trademark, legalAddress, isUnknown) 
            values ({x['id']}, "{x['name']}", "{x['fineName']}", {x['ogrn']}, "{x['trademark']}", "{x['legalAddress']}", {x['isUnknown']})''')
        conn.commit()

    return None


def insert_articul(df: pd.DataFrame) -> None:

    df.to_sql(name='articuls', con=conn, if_exists='append', index=False)

    return None


def recollection(flag: bool=False, table: str='articuls') -> None:
    if flag:
        conn.execute(f'''
                     CREATE TABLE temp_table as SELECT DISTINCT * FROM {table}
                     ''')
        
        conn.execute(f'''
                     DROP TABLE {table}
                     ''')
        
        conn.execute(f'''
                     ALTER TABLE temp_table RENAME TO {table}
                     ''')
        
        conn.commit()
    return None


