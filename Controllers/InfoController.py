from telebot.types import Message

from Bot import bot
from Model.DB import db

from Common import keyboards, answers


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
