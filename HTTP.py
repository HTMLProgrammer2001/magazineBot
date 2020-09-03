import requests
from time import time
from json import loads

import Common.config as config


class HTTP:
    filtersCache = {'value': None, 'lastTime': 0}

    def getFilters(self):
        if self.filtersCache['value'] and self.filtersCache['lastTime'] > time() - 3600:
            return self.filtersCache['value']

        response = requests.get(config.api_get_filters)

        if response.ok:
            print(response.text)

            self.filtersCache = {
                'value': loads(response.text),
                'lastTime': time()
            }

            return self.filtersCache['value']

    def getProducts(self, filters: dict, page: int = 1):
        print('Get products')

        response = requests.post(f"{config.api_get_products}?page={page}", json=filters)

        if response.ok:
            print(response.text)

            return loads(response.text)

        else:
            print(response.content)
