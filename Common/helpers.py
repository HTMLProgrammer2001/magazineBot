from json import loads

from Model.DB import db
from Common import keyboards, answers, config
from Bot import bot


# filter user function
def userHasState(state: int):
    return lambda message: db.userHasState(message.chat.id, state)


# parse price range from format %from%-%to%
def parseRange(r: str):
    priceRangeStr = r.replace(' ', '').split('-')
    priceRange = [float(item) for item in priceRangeStr]

    if len(priceRange) != 2:
        raise Exception('Invalid range')

    return priceRange


# func that return array of clothes sizes
def getSizes():
    return ['XS', 'S', 'M', 'L', 'XL']


# parse message from user filters
def parseFilters(userFilters: dict) -> dict:
    # default filters data
    filtersData = {
        'category': '<b>Category:</b> All\n',
        'size': '<b>Size:</b> All\n',
        'color': '<b>Color:</b> All\n',
        'price': '<b>Price:</b> All'
    }

    # set user filters data

    if userFilters.get('categories'):
        filtersData['category'] = '<b>Category:</b> {}\n'.format(userFilters.get('categories'))

    if userFilters.get('size'):
        filtersData['size'] = '<b>Size:</b> {}\n'.format(userFilters.get('size'))

    if userFilters.get('color'):
        filtersData['color'] = '<b>Color:</b> {}\n'.format(userFilters.get('color'))

    pRange = userFilters.get('priceRange')
    if pRange:
        filtersData['price'] = '<b>Price range: </b>'.format(
            str(pRange['from']) + '-' + str(pRange['to'])
        )

    return filtersData


# func that send one product
def sendProduct(userID: str, product: dict):
    product['colors'] = ', '.join(
        loads(product['colors']) if isinstance(product['colors'], str) else product['colors']
    )

    product['sizes'] = ', '.join(
        loads(product['sizes']) if isinstance(product['sizes'], str) else product['sizes']
    )

    reply = keyboards.linkKeyboard(product['name'], 'https://google.com')

    bot.send_photo(userID, f"{config.images_base_url}/{product['photo']}")
    #bot.send_photo(userID, 'https://i.insider.com/5eda82ae3ad8617d4e1c0b2e?width=1100&format=jpeg&auto=webp')

    bot.send_message(
        userID,
        answers.productItem.format(**product),
        reply_markup=reply
    )
