from telebot import TeleBot

from Common import config


bot = TeleBot(config.token, parse_mode="html")
