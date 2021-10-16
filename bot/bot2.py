import logging
from queue import PriorityQueue
#import pandas as pd
#import yfinance as yf
#import numpy as np
import redis
import json 
#import pandas_datareader as web
#import matplotlib.pyplot as plt
#import telebot
#import config
#from pypfopt.expected_returns import mean_historical_return
#from pypfopt import risk_models 
#from pypfopt import expected_returns
#from pypfopt.cla import CLA
#import pypfopt.plotting as pplt
#from matplotlib.ticker import FuncFormatter
#from pypfopt.risk_models import CovarianceShrinkage
#from pypfopt.efficient_frontier import EfficientFrontier
#from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton

import finance
import portfolio

from datetime import datetime
import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

#TOKEN = API_KEY
#bot = telebot.TeleBot(config.TOKEN)

#collect_companies = False
finSector = False
fin_list = []

PROXY = {
    'proxy_url': 'socks5://t1.learn.python.ru:1080',
    'urllib3_proxy_kwargs': {
        'username': 'learn',
        'password': 'python'
    }
}

conn = redis.Redis('localhost')
finance_dict = conn.hgetall("finance_dict") #.items()
new_finance_dict = {}
finance_comp_name = []
for key, value in finance_dict.items():
    new_finance_dict[key.decode('utf-8')] = value.decode('utf-8')
print(new_finance_dict)
#print(finance_dict)
#print(type(finance_dict))
for key, value in finance_dict.items():
    finance_comp_name.append(key.decode('utf-8'))



def greet_user(update, context):
    print("Вызван /start")
    update.message.reply_text(
        f"Привет! Выбери сектор.",
        reply_markup=main_keyboard()
    )

def main_keyboard():
    return ReplyKeyboardMarkup([['Финансы']])

def next():
    return ReplyKeyboardMarkup([['Другой сектор']])

#def next():
#    return ReplyKeyboardMarkup([['Все']])

   
#def help_command(message):  
 #   keyboard = telebot.types.InlineKeyboardMarkup()  
  #  keyboard.add(  
   #     telebot.types.InlineKeyboardButton(  
    #        'Message the developer', url='telegram.me/artiomtb'  
  #)  
   # )  
    #bot.send_message(  
     #   message.chat.id, 
      #  '1) Выбери сектор, акции которого тебе интересны.\n' + 
      #  '2) Выбери до (кол-во) компаний, интресеных тебе в данном сеторе.\n'+
       # '3) После получения состава портфеля реализуй команду /my_budget_portfolio , чтобы узнать количество акций, которые ты можешь купить относительно твоего бюджета.\n'+
       # '4) Реализуй команду /my_portfolio_stat чтобы узнать краткий свод статистики по своему портфелю.\n'+
       # '5) Реализуй команду /my_portfolio_chart чтобы посмотреть график твоего портфеля и диаграмму распределения акций в нем.'+
       # reply_markup = keyboard
   # )

def finance_handler(update, context):
    text = update.message.text
    global finSector
    finSector = True
    print(finSector)
    my_keyboard = ReplyKeyboardMarkup([['Финансы']], True)
    update.message.reply_text(f"{'В секторе финансы я знаю такие компании:'} {', '.join(finance_comp_name)}", reply_markup=next())
    return finSector

def collecting_user_data(update, context):
    global finSector
    global fin_list
    print(finSector)
    user_input = update.message.text
    if finSector:
        fin_list.append(user_input)
        update.message.reply_text(f"{'Ваше сообщение:'} {', '.join(fin_list)}", reply_markup=next())
    else:
        print('finance button off')
    return None
      
def tic(update, context):   
    tic_list = []
    print("FIN LUST", fin_list)
    print("finance_dict", type(new_finance_dict))
    for name in fin_list:
        tic_list.append(new_finance_dict.get(name))
    print("TIC LIST", tic_list)
    update.message.reply_text(f"{'Ваши тикеры:'} {', '.join(tic_list)}", reply_markup=next())
    print(tic_list)
        
    

#def get_tic(update, list_input_user):
 #   tic_list = []
  #  for name in list_input_user:
   #     tic_list.append(finance_dict[name])
   # print (tic_list)
   # update.message.reply_text(tic_list)


def test_func(update, context):
    text = update.message.text
    my_keyboard = ReplyKeyboardMarkup([['Другой сектор']], True)
    #update.message.reply_text(f"{'Ваше сообщение:'} {', '.join(list_input_user)}", reply_markup=next())


def main():
    mybot = Updater(settings.API_KEY, use_context=True, request_kwargs=PROXY)
    dp = mybot.dispatcher
    #if collect_companies:
     #   dp.add_handler(MessageHandler(Filters.text, talk_to_me_2))
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.regex('^Финансы'), finance_handler))
    #dp.add_handler(MessageHandler(Filters.text, talk_to_me_2))
    dp.add_handler(MessageHandler(Filters.regex('^Другой сектор'), test_func))
    dp.add_handler(CommandHandler("tic", tic))
    dp.add_handler(MessageHandler(Filters.text, collecting_user_data))

    #dp.add_handler(CommandHandler("help", help_command))

    # dp.add_handler(MessageHandler(Filters.text, portfolio_construct))
    # dp.add_handler(MessageHandler(Filters.text, talk_to_me_2))
    #dp.add_handler(CommandHandler("my_budget_portfolio", my_budget_portfolio))
    #dp.add_handler(CommandHandler("my_portfolio_stat", my_portfolio_stat))
    #dp.add_handler(CommandHandler("my_portfolio_chart", my_portfolio_chart))

    logging.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()