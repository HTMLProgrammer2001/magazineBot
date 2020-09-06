from telebot.types import Message

from Bot import bot
from Model.DB import db
from Model.HTTP import http

from Controllers.ShowController import getProducts

from Common import keyboards, answers, states
from Common.helpers import userHasState, parseRange, getSizes, parseFilters


@bot.message_handler(commands=['products'])
def products(message: Message):
    reply = keyboards.isFilterProducts()

    # send question and create user
    bot.send_message(message.chat.id, answers.productStart, reply_markup=reply)
    db.createUser(message.chat.id, filters=dict())


@bot.message_handler(func=userHasState(states.PRODUCTS_START))
def willFilter(message: Message):
    if message.text == 'Yes':
        setFiltersStart(message)

    elif message.text == 'No':
        # show all products
        db.changeUserState(message.chat.id, state=states.SHOW_PRODUCTS, filters=dict(), page=1)

        # send products
        getProducts(message)

    else:
        bot.send_message(
            message.chat.id,
            answers.invalidValue
        )


@bot.message_handler(commands=['setFilters'])
def setFiltersStart(message: Message):
    # start asking of filters
    db.changeUserState(message.chat.id, state=states.FILTER_CATEGORY, filters=dict(), page=1)

    # make keyboard of categories
    filters = http.getFilters()
    reply = keyboards.listKeyboard(map(lambda item: item['name'], filters['categories']))

    bot.send_message(message.chat.id, answers.filterCategory, reply_markup=reply)


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
    db.changeUserState(message.chat.id, state=states.FILTER_SIZE, filters=userFilters)

    # send next step
    bot.send_message(
        message.chat.id,
        answers.filterSize,
        reply_markup=keyboards.listKeyboard(getSizes())
    )


@bot.message_handler(func=userHasState(states.FILTER_SIZE))
def filterSize(message: Message):
    userFilters: dict = db.getUser(message.chat.id)[2]

    if message.text != '.':
        if message.text in getSizes():
            # change db data
            userFilters['size'] = message.text

        else:
            bot.send_message(
                message.chat.id,
                answers.filterSizeInvalid
            )

            return

    # change db data
    db.changeUserState(message.chat.id, state=states.FILTER_COLOR, filters=userFilters)

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
    db.changeUserState(message.chat.id, state=states.FILTER_PRICE, filters=userFilters)

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
            priceRange = parseRange(message.text)

            # set data to db
            userFilters['priceRange'] = {
                'from': min(priceRange),
                'to': max(priceRange)
            }

        except Exception:
            bot.send_message(message.chat.id, answers.filterPriceInvalid)
            return

    # get products
    db.changeUserState(message.chat.id, state=states.SHOW_PRODUCTS, filters=userFilters)
    getProducts(message)


@bot.message_handler(commands=['filters'])
def getFilters(message: Message):
    user = db.getUser(message.chat.id)

    if not user:
        # send no filters response
        bot.send_message(message.chat.id, answers.noFilters)
        return

    userFilters = user[2]
    filtersData = parseFilters(userFilters)

    # send response
    bot.send_message(message.chat.id, answers.userFilters.format(**filtersData))
