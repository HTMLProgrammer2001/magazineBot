import requests
from time import time
from json import loads

import Common.config as config


class HTTP:
    filters = None
    lastFilterRequest = 0

    def getFilters(self):
        if self.filters and self.lastFilterRequest > time() - 3600:
            return self.filters

        response = requests.get(config.api_get_filters)

        if response.ok:
            print(response.text)

            self.filters = loads(response.text)
            self.lastFilterRequest = time()

            return self.filters
