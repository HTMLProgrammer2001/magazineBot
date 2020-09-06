from Bot import bot
from Common import answers
from Common.keyboards import removeKeyBoard

import Controllers.InfoController
import Controllers.FilterController
import Controllers.SearchController
import Controllers.ShowController


@bot.message_handler()
def notFound(message):
    bot.reply_to(message, answers.notFound, reply_markup=removeKeyBoard())
