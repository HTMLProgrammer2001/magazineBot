from telebot.types import Message

from Bot import bot
from Model.DB import db
from Model.HTTP import http

from Common import states, keyboards, answers, helpers


@bot.message_handler(commands=['next'], func=lambda m: db.hasUser(m.chat.id))
def getNextProducts(message: Message):
    user = db.getUser(message.chat.id)
    page = user[3] + 1

    db.changeUserState(message.chat.id, page=page)
    getProducts(message)


@bot.message_handler(commands=['prev'], func=lambda m: db.hasUser(m.chat.id))
def getPrevProducts(message: Message):
    user = db.getUser(message.chat.id)
    page = user[3] - 1

    db.changeUserState(message.chat.id, page=page)
    getProducts(message)


@bot.message_handler(commands=['get'])
def getProducts(message: Message):
    user = db.getUser(message.chat.id)

    if not user:
        db.createUser(message.chat.id, states.SHOW_PRODUCTS)
        user = db.getUser(message.chat.id)

    page = user[3]

    print(page)

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
        helpers.sendProduct(message.chat.id, product)
