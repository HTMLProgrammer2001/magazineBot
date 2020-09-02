import telebot
from telebot.types import Message

from Common import config, answers, states, keyboards
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
        bot.send_message(message.chat.id, answers.resetSuccess, reply_markup=keyboards.removeKeyBoard())
    else:
        bot.send_message(message.chat.id, answers.resetFailure, reply_markup=keyboards.removeKeyBoard())


@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.send_message(message.chat.id, answers.start, reply_markup=keyboards.removeKeyBoard())


@bot.message_handler(commands=['about'])
def about(message: Message):
    bot.send_message(message.chat.id, answers.about, reply_markup=keyboards.removeKeyBoard())


@bot.message_handler(commands=['contacts'])
def contacts(message: Message):
    bot.send_message(message.chat.id, answers.contacts, reply_markup=keyboards.removeKeyBoard())


@bot.message_handler(commands=['site'])
def site(message: Message):
    bot.send_message(message.chat.id, answers.site, reply_markup=keyboards.removeKeyBoard())


@bot.message_handler(commands=['products'])
def products(message: Message):
    reply = keyboards.isFilterProducts()

    # send question and create user
    bot.send_message(message.chat.id, answers.productStart, reply_markup=reply)
    db.createUser(message.chat.id)


@bot.message_handler(func=userHasState(states.PRODUCTS_START))
def willFilter(message: Message):
    if message.text == 'Yes':
        # start asking of filters
        db.changeUserState(message.chat.id, states.FILTER_CATEGORY)

        # make keyboard of categories
        filters = http.getFilters()
        reply = keyboards.listKeyboard(map(lambda item: item['name'], filters['categories']))

        bot.send_message(message.chat.id, answers.filterCategory, reply_markup=reply)

    elif message.text == 'No':
        # show all products
        db.changeUserState(message.chat.id, states.SHOW_PRODUCTS)

        reply = keyboards.removeKeyBoard()
        bot.send_message(message.chat.id, answers.showProducts, reply_markup=reply)

    else:
        bot.send_message(
            message.chat.id,
            answers.invalidValue
        )


@bot.message_handler(func=userHasState(states.FILTER_CATEGORY))
def filterCategory(message: Message):
    # skip this filter
    if message.text == '.':
        userDetails: dict = db.getUser(message.chat.id)[2]
        db.changeUserState(message.chat.id, states.FILTER_SIZE, userDetails)

        return

    # get filters
    filters = http.getFilters()
    categories: list = list(map(lambda item: item['name'], filters['categories']))

    # find category
    index = categories.index(message.text)

    if index != -1:
        # add filter to db
        userDetails: dict = db.getUser(message.chat.id)[2]
        userDetails['filterCategory'] = filters['categories'][index]['id']

        db.changeUserState(message.chat.id, states.FILTER_SIZE, userDetails)
        bot.send_message(
            message.chat.id,
            answers.filterSize,
            reply_markup=keyboards.listKeyboard(sizes)
        )

    else:
        bot.send_message(
            message.chat.id,
            answers.filterCategoryInvalid
        )


@bot.message_handler(func=userHasState(states.FILTER_SIZE))
def filterSize(message: Message):
    # skip this filter
    if message.text == '.':
        userDetails: dict = db.getUser(message.chat.id)[2]
        db.changeUserState(message.chat.id, states.FILTER_COLOR, userDetails)

        return

    if message.text in sizes:
        # change db data
        userDetails: dict = db.getUser(message.chat.id)[2]
        userDetails['filterSize'] = message.text

        db.changeUserState(message.chat.id, states.FILTER_COLOR, userDetails)

        filters = http.getFilters()
        colors = filters['colors']

        bot.send_message(
            message.chat.id,
            answers.filterColor,
            reply_markup=keyboards.listKeyboard(colors)
        )
    else:
        bot.send_message(
            message.chat.id,
            answers.filterSizeInvalid
        )


@bot.message_handler(func=userHasState(states.FILTER_COLOR))
def filterColor(message: Message):
    # skip this filter
    if message.text == '.':
        userDetails: dict = db.getUser(message.chat.id)[2]
        db.changeUserState(message.chat.id, states.FILTER_PRICE, userDetails)
        return

    filters = http.getFilters()
    colors = filters['colors']

    if message.text in colors:
        # change db data
        userDetails: dict = db.getUser(message.chat.id)[2]
        userDetails['filterColor'] = message.text

        db.changeUserState(message.chat.id, states.FILTER_PRICE, userDetails)

        bot.send_message(
            message.chat.id,
            answers.filterPrice,
            reply_markup=keyboards.removeKeyBoard()
        )

    else:
        bot.send_message(
            message.chat.id,
            answers.filterColorInvalid
        )


@bot.message_handler(func=userHasState(states.FILTER_PRICE))
def filterPrice(message: Message):
    # skip this filter
    if message.text == '.':
        userDetails: dict = db.getUser(message.chat.id)[2]
        db.changeUserState(message.chat.id, states.SHOW_PRODUCTS, userDetails)
        return

    try:
        # parse range
        priceRangeStr = message.text.replace(' ', '').split('-')
        priceRange = [float(item) for item in priceRangeStr]

        if len(priceRange) != 2:
            raise Exception('Invalid range')

        # set data to db
        userDetails: dict = db.getUser(message.chat.id)[2]
        userDetails['filterPrice'] = {
            'from': min(priceRange),
            'to': max(priceRange)
        }

        db.changeUserState(message.chat.id, states.SHOW_PRODUCTS, userDetails)
        bot.send_message(
            message.chat.id,
            answers.showProducts,
            reply_markup=keyboards.removeKeyBoard()
        )

    except Exception:
        bot.send_message(message.chat.id, answers.filterPriceInvalid)


@bot.message_handler()
def notFound(message: Message):
    bot.reply_to(message, answers.notFound, reply_markup=keyboards.removeKeyBoard())


if __name__ == '__main__':
    print('Bot started')
    bot.infinity_polling()
