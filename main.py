import telebot
from telebot.types import Message

from Common import config, answers, states, keyboards, helpers
from DB import DB
from HTTP import HTTP

# declare global vars
bot = telebot.TeleBot(config.token, parse_mode="html")
db = DB()
http = HTTP()

# declare goods sizes
sizes = ['XS', 'S', 'M', 'L', 'XL']


# filter user function
def userHasState(state: int):
    return lambda message: db.userHasState(message.chat.id, state)


# reset user state
@bot.message_handler(commands=['reset'])
def reset(message):
    if db.hasUser(message.chat.id):
        db.deleteUser(message.chat.id)
        bot.send_message(
            message.chat.id,
            answers.resetSuccess,
            reply_markup=keyboards.removeKeyBoard()
        )
    else:
        bot.send_message(
            message.chat.id,
            answers.resetFailure,
            reply_markup=keyboards.removeKeyBoard()
        )


@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.send_message(
        message.chat.id,
        answers.start,
        reply_markup=keyboards.removeKeyBoard()
    )


@bot.message_handler(commands=['about'])
def about(message: Message):
    bot.send_message(
        message.chat.id,
        answers.about,
        reply_markup=keyboards.removeKeyBoard()
    )


@bot.message_handler(commands=['contacts'])
def contacts(message: Message):
    bot.send_message(
        message.chat.id,
        answers.contacts,
        reply_markup=keyboards.removeKeyBoard()
    )


@bot.message_handler(commands=['site'])
def site(message: Message):
    bot.send_message(
        message.chat.id,
        answers.site,
        reply_markup=keyboards.removeKeyBoard()
    )


@bot.message_handler(commands=['products'])
def products(message: Message):
    reply = keyboards.isFilterProducts()

    # send question and create user
    bot.send_message(message.chat.id, answers.productStart, reply_markup=reply)
    db.createUser(message.chat.id, filters=dict())


@bot.message_handler(func=userHasState(states.PRODUCTS_START))
def willFilter(message: Message):
    if message.text == 'Yes':
        # start asking of filters
        db.changeUserState(message.chat.id, states.FILTER_CATEGORY, dict(), 1)

        # make keyboard of categories
        filters = http.getFilters()
        reply = keyboards.listKeyboard(map(lambda item: item['name'], filters['categories']))

        bot.send_message(message.chat.id, answers.filterCategory, reply_markup=reply)

    elif message.text == 'No':
        # show all products
        db.changeUserState(message.chat.id, states.SHOW_PRODUCTS, filters=dict(), page=1)

        # send products
        getProducts(message)

    else:
        bot.send_message(
            message.chat.id,
            answers.invalidValue
        )


@bot.message_handler(func=userHasState(states.FILTER_CATEGORY))
def filterCategory(message: Message):
    userFilters: dict = db.getUser(message.chat.id)[2]
    userFilters['categories'] = []

    if message.text != '.':
        # get filters
        filters = http.getFilters()
        categories: list = list(map(lambda item: item['name'], filters['categories']))

        # find category
        index = categories.index(message.text)

        if index != -1:
            # add filter to db
            catID = filters['categories'][index]['id']
            userFilters['categories'] = {catID: True}

        else:
            bot.send_message(
                message.chat.id,
                answers.filterCategoryInvalid
            )

            return

    # set new data to db
    db.changeUserState(message.chat.id, states.FILTER_SIZE, userFilters)

    # send next step
    bot.send_message(
        message.chat.id,
        answers.filterSize,
        reply_markup=keyboards.listKeyboard(sizes)
    )


@bot.message_handler(func=userHasState(states.FILTER_SIZE))
def filterSize(message: Message):
    userFilters: dict = db.getUser(message.chat.id)[2]

    if message.text != '.':
        if message.text in sizes:
            # change db data
            userFilters['size'] = message.text

        else:
            bot.send_message(
                message.chat.id,
                answers.filterSizeInvalid
            )

            return

    # change db data
    db.changeUserState(message.chat.id, states.FILTER_COLOR, userFilters)

    # get next step data
    filters = http.getFilters()
    colors = filters['colors']

    # send next step
    bot.send_message(
        message.chat.id,
        answers.filterColor,
        reply_markup=keyboards.listKeyboard(colors)
    )


@bot.message_handler(func=userHasState(states.FILTER_COLOR))
def filterColor(message: Message):
    userFilters: dict = db.getUser(message.chat.id)[2]

    if message.text != '.':
        filters = http.getFilters()
        colors = filters['colors']

        if message.text in colors:
            # change db data
            userFilters['color'] = message.text

        else:
            bot.send_message(
                message.chat.id,
                answers.filterColorInvalid
            )

            return

    # set data to db
    db.changeUserState(message.chat.id, states.FILTER_PRICE, userFilters)

    # send next step
    bot.send_message(
        message.chat.id,
        answers.filterPrice,
        reply_markup=keyboards.removeKeyBoard()
    )


@bot.message_handler(func=userHasState(states.FILTER_PRICE))
def filterPrice(message: Message):
    userFilters: dict = db.getUser(message.chat.id)[2]

    if message.text != '.':
        try:
            # parse range
            priceRange = helpers.parseRange(message.text)

            # set data to db
            userFilters['priceRange'] = {
                'from': min(priceRange),
                'to': max(priceRange)
            }

        except Exception:
            bot.send_message(message.chat.id, answers.filterPriceInvalid)
            return

    # get products
    db.changeUserState(message.chat.id, states.SHOW_PRODUCTS, userFilters)
    getProducts(message)


@bot.message_handler(commands=['next'])
def getNextProducts(message: Message):
    user = db.getUser(message.chat.id)
    page = user[3] + 1

    db.changeUserState(message.chat.id, page=page)
    getProducts(message)


@bot.message_handler(commands=['prev'])
def getPrevProducts(message: Message):
    user = db.getUser(message.chat.id)
    page = user[3] - 1

    db.changeUserState(message.chat.id, page=page)
    getProducts(message)


@bot.message_handler(commands=['get'])
def getProducts(message: Message):
    user = db.getUser(message.chat.id)
    page = user[3]

    if page <= 0:
        db.changeUserState(message.chat.id, page=1)

        bot.send_message(
            message.chat.id,
            answers.outOfRange,
            reply_markup=keyboards.removeKeyBoard()
        )

        return

    httpProduct = http.getProducts(user[2], page)

    if not len(httpProduct['data']):
        bot.send_message(message.chat.id, answers.noData)
        return

    for product in httpProduct['data']:
        bot.send_message(message.chat.id, answers.productItem.format(**product))


@bot.message_handler()
def notFound(message: Message):
    bot.reply_to(message, answers.notFound, reply_markup=keyboards.removeKeyBoard())


if __name__ == '__main__':
    print('Bot started')
    bot.infinity_polling()
