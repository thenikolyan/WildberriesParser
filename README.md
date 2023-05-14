# WildberriesParser
The parser was created to quickly obtain information using requests from the site https://www.wildberries.ru


# Instructions for use

If uoy need common information from brand or catalog. You have to create object of Product class, so the class needs to pass a link as an argument

```python
import pandas as pd

from utils.products import Product
from utils.catalog import Catalog

if __name__ == '__main__':
    url = 'https://www.wildberries.ru/catalog/igrushki/antistress'
    products = Product(url)
```

Then you need to run the information collection function "", pass it as an argument the number of pages for parsing. (You can submit any amount, but remember that wildberries do not upload information after [page 100](https://www.wildberries.ru/catalog/igrushki/antistress&page=100))

```python
    df = products.multiprocess(5)
    df.to_excel('filename.xlsx', index=False)
```

As a result, you get excel file like this:
(https://github.com/thenikolyan/WildberriesParser/assets/48589418/ffbb4d4d-835c-407d-9477-3e4736e687f0)

(https://github.com/thenikolyan/WildberriesParser/assets/48589418/29c34154-5830-4545-911f-bf61aa29febc)


