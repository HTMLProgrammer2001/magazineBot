import os


token = os.environ.get('TOKEN')

dbConnection = {
    'user': os.environ.get('DB_USER') or 'root',
    'host': os.environ.get('DB_HOST') or '127.0.0.1',
    'password': os.environ.get('DB_PASSWORD') or '',
    'database': os.environ.get('DB_DATABASE') or 'react_magazine'
}

# communication
site_url = os.environ.get('SITE_URL') or 'https://magazinel.herokuapp.com/'
mail = 'cssuperpy@gmail.com'
phone = '+380666754334'

# API
api_base_url = os.environ.get('API_URL') or 'https://magazinel.herokuapp.com/api'
api_get_filters = f'{api_base_url}/productFilters'
api_get_products = f'{api_base_url}/getProducts'
api_find = f'{api_base_url}/find'

images_base_url = f'{site_url}image'
