from telebot.types import Message

from Bot import bot
from Model.DB import db
from Model.HTTP import http
from Common import answers, keyboards, helpers, states


@bot.message_handler(commands=['find'])
def find(message: Message):
    db.changeUserState(message.chat.id, state=states.FIND)
    bot.send_message(message.chat.id, answers.findMessage, reply_markup=keyboards.removeKeyBoard())


@bot.message_handler(func=helpers.userHasState(states.FIND))
def enterFind(message: Message):
    if not message.text:
        # send error message
        bot.send_message(message.chat.id, answers.findInvalid)
        return

    # change state to show
    db.changeUserState(message.chat.id, state=states.SHOW_PRODUCTS)

    # find products
    products: dict = http.findProducts(message.text)

    if not len(products.get('data')):
        bot.send_message(message.chat.id, answers.notFound, reply_markup=keyboards.removeKeyBoard())

    # show products
    for product in products.get('data'):
        helpers.sendProduct(message.chat.id, product)
