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
![Картинка][image1]
![Картинка][image2]
![Картинка][image3]

[image1]: C:/Users/nikol/Downloads/photo_2023-05-14_16-15-34.jpg
[image2]: //placehold.it/200x100
[image3]: //placehold.it/150x100
