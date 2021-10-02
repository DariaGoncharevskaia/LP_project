import logging
import pandas as pd
import yfinance as yf
import numpy as np
import redis
import json
import ephem 
#import finance
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import settings
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


PROXY = {
    'proxy_url': 'socks5://t1.learn.python.ru:1080',
    'urllib3_proxy_kwargs': {
        'username': 'learn',
        'password': 'python'
    }
}


conn = redis.Redis('localhost')
finance_comp_name = []
for key, value in conn.hgetall("finance_dict").items():
    finance_comp_name.append(key.decode('utf-8'))


def main_keyboard():
    return ReplyKeyboardMarkup([['Финансы']])

def greet_user(update, context):
    print("Вызван /start")
    update.message.reply_text(
        f"Привет! Выбери сектор.",
        reply_markup=main_keyboard()
    )

def talk_to_me(update, context):
    text = update.message.text
    my_keyboard = ReplyKeyboardMarkup([['Финансы']])
    update.message.reply_text(f"{'В секторе финансы я знаю такие компании:'} {', '.join(finance_comp_name)}", reply_markup=main_keyboard())


def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()