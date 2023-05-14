# WildberriesParser
The parser was created to quickly obtain information using requests from the site https://www.wildberries.ru


# Instructions for use

## Products

If uoy need common information from brand or catalog. You have to create object of Product class, so the class needs to pass a link as an argument

```python
import pandas as pd

from utils.products import Product
from utils.catalog import Catalog

if __name__ == '__main__':
    url = 'https://www.wildberries.ru/catalog/igrushki/antistress'
    products = Product(url)
```

Then you need to run the information collection function `multiprocess`, pass it as an argument the number of pages for parsing. (You can submit any amount, but remember that wildberries do not upload information after [page 100](https://www.wildberries.ru/catalog/igrushki/antistress&page=100))

```python
    df = products.multiprocess(5)
    df.to_excel('filename.xlsx', index=False)
```

As a result, you get excel file like this:
![first](https://github.com/thenikolyan/WildberriesParser/assets/48589418/ffbb4d4d-835c-407d-9477-3e4736e687f0)

![second](https://github.com/thenikolyan/WildberriesParser/assets/48589418/29c34154-5830-4545-911f-bf61aa29febc)


## Additional Information

### Other sellers

`Attention! This feature is very expensive, please be patient.`

If you want to know the analogues sold by other sellers. You need to specify the mode of operation and pass the `DataFrame` with the `id` column, where the articles for which you are looking for analogues are registered.

```python
    other_products = products.multiprocess(df, mode='other_sellers')
    other_products.to_excel('filename.xlsx', index=False)
```

As a result, you will have a file with columns `id` and `brother` article and analogue, respectively.


### Purchased products

If you want to know how many times a product has been bought, you need to use the `purchased_products` mode. You must submit a `DataFrame` as input, with the `id` column, where the articles for which you want to know information are indicated.

```python
    purchased_products = products.multiprocess(df, mode='purchased_products')
    purchased_products.to_excel('filename.xlsx', index=False)
```
As a result, you will have a file with columns `nmId` and `qnt` article and number, respectively.
