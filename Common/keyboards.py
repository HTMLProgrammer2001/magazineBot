from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup


def isFilterProducts():
    keyboard = ReplyKeyboardMarkup()

    okBtn = KeyboardButton('Yes')
    rejectBtn = KeyboardButton('No')

    keyboard.row(okBtn, rejectBtn)

    return keyboard


def listKeyboard(items):
    if items is None:
        items = []

    buttons = []
    keyboard = ReplyKeyboardMarkup()

    for item in items:
        buttons.append(KeyboardButton(item))

    keyboard.add(*buttons)

    return keyboard


def linkKeyboard(message: str, link: str):
    keyboard = InlineKeyboardMarkup()

    button = InlineKeyboardButton(message, url=link, callback_data=None)
    keyboard.add(button)

    return keyboard


def removeKeyBoard():
    return ReplyKeyboardRemove()
