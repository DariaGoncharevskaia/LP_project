import matplotlib
# matplotlib.use('Agg')
import logging
import pandas as pd
import yfinance as yf
import numpy as np
import markdown2
import redis
import json 
import os
import scipy
import pandas_datareader as web
import matplotlib.pyplot as plt
import pypfopt.plotting as pplt
import statsmodels.api as sm
import requests
import math

from pprint import pprint
from queue import PriorityQueue
from typing import MutableMapping
from scipy import stats
from pypfopt.expected_returns import mean_historical_return
from pypfopt import risk_models, expected_returns
from pypfopt.cla import CLA
from pypfopt.efficient_frontier import EfficientFrontier
from matplotlib.ticker import FuncFormatter
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup

import finance
import portfolio
import settings


logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')


collect_companies = False
companies_list = []
tic_list= []

PROXY = {
    'proxy_url': 'socks5://t1.learn.python.ru:1080',
    'urllib3_proxy_kwargs': {
        'username': 'learn',
        'password': 'python'
    }
}

conn = redis.Redis('localhost')
finance_dict = conn.hgetall("finance_dict")
new_finance_dict = {}
finance_comp_name = []
for key, value in finance_dict.items():
    new_finance_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in finance_dict.items():
    finance_comp_name.append(key.decode('utf-8'))

conn = redis.Redis('localhost')
discretionary_dict = conn.hgetall("discretionary_dict") 
new_discretionary_dict = {}
discretionary_comp_name = []
for key, value in discretionary_dict.items():
    new_discretionary_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in discretionary_dict.items():
    discretionary_comp_name.append(key.decode('utf-8'))

conn = redis.Redis('localhost')
energy_dict = conn.hgetall("energy_dict") 
new_energy_dict = {}
energy_comp_name = []
for key, value in energy_dict.items():
    new_energy_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in energy_dict.items():
    energy_comp_name.append(key.decode('utf-8'))

conn = redis.Redis('localhost')
healthcare_dict = conn.hgetall("healthcare_dict") 
new_healthcare_dict = {}
healthcare_comp_name = []
for key, value in healthcare_dict.items():
    new_healthcare_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in healthcare_dict.items():
    healthcare_comp_name.append(key.decode('utf-8'))

conn = redis.Redis('localhost')
industrials_dict = conn.hgetall("industrials_dict") 
new_industrials_dict = {}
industrials_comp_name = []
for key, value in industrials_dict.items():
    new_industrials_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in industrials_dict.items():
    industrials_comp_name.append(key.decode('utf-8'))

conn = redis.Redis('localhost')
materials_dict = conn.hgetall("materials_dict") 
new_materials_dict = {}
materials_comp_name = []
for key, value in materials_dict.items():
    new_materials_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in materials_dict.items():
    materials_comp_name.append(key.decode('utf-8'))

conn = redis.Redis('localhost')
staples_dict = conn.hgetall("staples_dict") 
new_staples_dict = {}
staples_comp_name = []
for key, value in staples_dict.items():
    new_staples_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in staples_dict.items():
    staples_comp_name.append(key.decode('utf-8'))

conn = redis.Redis('localhost')
technology_dict = conn.hgetall("technology_dict") 
new_technology_dict = {}
technology_comp_name = []
for key, value in technology_dict.items():
    new_technology_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in technology_dict.items():
    technology_comp_name.append(key.decode('utf-8'))

conn = redis.Redis('localhost')
telecom_dict = conn.hgetall("telecom_dict") 
new_telecom_dict = {}
telecom_comp_name = []
for key, value in telecom_dict.items():
    new_telecom_dict[key.decode('utf-8')] = value.decode('utf-8')
for key, value in telecom_dict.items():
    telecom_comp_name.append(key.decode('utf-8'))

global_dict = {**new_discretionary_dict, **new_energy_dict, **new_finance_dict, 
**new_healthcare_dict, **new_industrials_dict, **new_materials_dict, **new_staples_dict,
**new_technology_dict, **new_telecom_dict}
global_keys = global_dict.keys()

def greet_user(update, context):
    print("Вызван /start")
    update.message.reply_text(
        f"Привет! Вызови команду /help.")

def help_command(update, context):   
    update.message.reply_text(
        f"1. Выбери сектор, акции которого тебе интересны.")
    update.message.reply_text(
        f"2.Выбери компании, которые тебе интересны, из предложенных списков(вводи название и отправляй).")
    update.message.reply_text(
        f"3. Используй команду /tic, чтобы получить список тикеров.")
    update.message.reply_text(
        f"4. Используй команду /portfolio, чтобы составить портфель из выбранных компаний.")
    update.message.reply_text(
        f"5. Используй команду /describe, чтобы получить описание портфеля.")
    update.message.reply_text(
        f"6. Используй команду /price, чтобы вывести график изменения цен, выбранных акций.")
    update.message.reply_text(
        f"7. Используй команду /budget, чтобы ввести сумму для расчета количества акций.")    
    update.message.reply_text(
        f"Если клавиатура снова понадобится, то вызови команду /keyboard.", 
        reply_markup= main_keyboard())

def get_keyboard(update, context):
    update.message.reply_text(
        f"Возвращаю клавиатуру.", 
        reply_markup= main_keyboard()
        )

def main_keyboard():
    return ReplyKeyboardMarkup([['Финансы'], ['Потреб'], ['Энергетика'], ['Телеком'],
    ['Материалы'], ['Технологии'], ['Здравоохранение'], ['Промышленность'], ['Ритэйл']])


def finance_handler(update, context):
    text = update.message.text
    global collect_companies 
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Финансы']], True)
    update.message.reply_text(\
    f"{'В секторе финансы я знаю такие компании:'} {', '.join(finance_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def discretionary_handler(update, context):
    text = update.message.text
    global collect_companies
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Потреб']], True)
    update.message.reply_text(\
    f"{'В секторе вторичной необходимости я знаю такие компании:'} {', '.join(discretionary_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def energy_handler(update, context):
    text = update.message.text
    global collect_companies
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Энергетика']], True)
    update.message.reply_text(\
    f"{'В секторе энергетика я знаю такие компании:'} {', '.join(energy_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def healthcare_handler(update, context):
    text = update.message.text
    global collect_companies
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Здравоохранение']], True)
    update.message.reply_text(\
    f"{'В секторе здравоохранение я знаю такие компании:'} {', '.join(healthcare_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def industrials_handler(update, context):
    text = update.message.text
    global collect_companies
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Промышленность']], True)
    update.message.reply_text(\
    f"{'В секторе промышленность я знаю такие компании:'} {', '.join(industrials_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def materials_handler(update, context):
    text = update.message.text
    global collect_companies
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Материалы']], True)
    update.message.reply_text(\
    f"{'В секторе материалы я знаю такие компании:'} {', '.join(materials_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def staples_handler(update, context):
    text = update.message.text
    global collect_companies
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Ритэйл']], True)
    update.message.reply_text(\
    f"{'В секторе розничной торговли я знаю такие компании:'} {', '.join(staples_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def technology_handler(update, context):
    text = update.message.text
    global collect_companies
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Технологии']], True)
    update.message.reply_text(\
    f"{'В секторе технологии я знаю такие компании:'} {', '.join(technology_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def tele_handler(update, context):
    text = update.message.text
    global collect_companies
    collect_companies = True
    my_keyboard = ReplyKeyboardMarkup([['Телеком']], True)
    update.message.reply_text(\
    f"{'В секторе телеком я знаю такие компании:'} {', '.join(telecom_comp_name)}",\
        reply_markup=main_keyboard())
    return collect_companies

def collecting_user_data(update, context):
    global collect_companies
    global companies_list
    print(collect_companies)
    user_input = update.message.text
    if collect_companies:
        if user_input not in companies_list:
            companies_list.append(user_input)
        else:
            update.message.reply_text(f"Такое название уже есть :(", reply_markup=main_keyboard())
        for el in companies_list:
            if el not in global_keys:
                update.message.reply_text('Ошибка в названии компании, попробуй еще раз :(',
                reply_markup=main_keyboard())
                companies_list.remove(el)
        update.message.reply_text(f'{"Компании:"} {", ".join(companies_list)}', \
             reply_markup=main_keyboard())
        return None
    else:
        print('button off')
        global budget
        budget = user_input
        print(budget)
        update.message.reply_text(f'{"Сумма:"} {budget}')
        update.message.reply_text(f'Для расчета вызовите команду /value')
    return budget  


def tic(update, context):   
    global tic_list 
    for name in companies_list:
        name_to_append = global_dict.get(name)
        if name_to_append not in tic_list:
            tic_list.append(name_to_append)
    print("TIC LIST", tic_list)
    update.message.reply_text(f'{"Тикеры:"} {", ".join(tic_list)}')
    return tic_list


def portfolio_construct(update, context):
    global data 
    global mu 
    global S 
    global ex 
    global weights
    global cleaned_weights
    global ef
    data = pd.DataFrame(columns=tic_list)
    today = datetime.today()

    for ticker in tic_list:
        data[ticker] = yf.download(ticker, start = today - timedelta(days=365), end=today) ['Adj Close']
    mu = mean_historical_return(data)
    S = risk_models.sample_cov(data)
    ef = EfficientFrontier(mu, S, weight_bounds = (0,1))
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    print(data)
    update.message.reply_text(f'{"*СОСТАВ ПОРТФЕЛЯ*"}', parse_mode='MarkdownV2')
    for key, value in cleaned_weights.items():
        update.message.reply_text(f'{"(Тикер: {0})  (Вес: {1})".format(key,value)}')


    cl_obj = CLA(mu, S)
    ax = pplt.plot_efficient_frontier(cl_obj, showfig = False)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.0%}'.format(x)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    plt.savefig('markovitz_chart', dpi=50)
    
    tickers =[]
    t_weights =[]

    for i in cleaned_weights:
  
        if cleaned_weights[i] > 0:
             t_weights.append(cleaned_weights[i])
             tickers.append(i)
    
    fig1, ax1 = plt.subplots()
    ax1.pie(t_weights, labels=tickers)
    ax1.axis('equal')
    patches, texts, auto = ax1.pie(t_weights, startangle=90, autopct='%1.1f%%' )
    plt.legend(patches, tickers, loc="best")
    plt.savefig('portfilio_chart.png', facecolor = 'blue', bbox_inches='tight', dpi=50 )

    ax2 = ((data.pct_change()+1).cumprod()).plot(figsize=(10, 7))
    plt.legend()
    plt.title("Adjusted Close Price", fontsize=16)
    plt.ylabel('Price', fontsize=14)
    plt.xlabel('Year', fontsize=14)
    plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)
    plt.savefig('price_chart.png', dpi = 50)

    # update.message.reply_text(f'{cleaned_weights}')
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open('portfilio_chart.png', 'rb'))
    # context.bot.send_photo(chat_id=chat_id, photo=open('price_chart.png', 'rb'))
    # context.bot.send_photo(chat_id=chat_id, photo=open('markovitz_chart', 'rb'))
    import os
    os.remove('portfilio_chart.png')
    print(cleaned_weights)
    print(f'построение графика')
    return  ax1
    return cleaned_weights

def describe(update, context):
    dis = ef.portfolio_performance(verbose=True)
    update.message.reply_text(f'{"*ОБЩИЕ ХАРАКТЕРИСТИКИ*"}', parse_mode='MarkdownV2')
    update.message.reply_text(f'{"Ожидаемая годовая прибыль:"} {format(dis[0]*100, ".1f")}{"%"}')
    update.message.reply_text(f'{"Годовая волатильность:"} {format(dis[1]*100, ".1f")}{"%"}')
    update.message.reply_text(f'{"Коэффициент Шарпа:"} {format(dis[2], ".1f")}')

def price_chart(update, context):
    ax2 = ((data.pct_change()+1).cumprod()).plot(figsize=(10, 7))
    plt.legend()
    plt.title("Adjusted Close Price", fontsize=16)
    plt.ylabel('Price', fontsize=14)
    plt.xlabel('Year', fontsize=14)
    plt.grid(which="major", color='k', linestyle='-.', linewidth=0.5)
    plt.savefig('price_chart.png', dpi = 50)
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id=chat_id, photo=open('price_chart.png', 'rb'))
    return ax2
   
def user_budget(update, context):
    global collect_companies
    collect_companies = False
    if collect_companies == False: 
        update.message.reply_text(f'{"Введите сумму в рублях."}')

def value_p(update, context):
    global budget
    global data_usd
    latest_prices1 = get_latest_prices(data)
    data_usd = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    usd = data_usd['Valute']['USD']
    usd = usd['Value']
    budget = int(budget)
    budget_usd = budget/usd
    tc = latest_prices1.index
    tc = tc.tolist()
    quant = {}
    for i in tc:
        if i[-3] == '.':
            latest_prices1[i] = latest_prices1[i]/usd
        quant[i] = math.floor((budget_usd*cleaned_weights[i])/latest_prices1[i])
        print(quant)
    
    update.message.reply_text(f'{"*Потратив*"} {budget} {"вы сможете купить акции"}', parse_mode='MarkdownV2')
    for i in quant:
        update.message.reply_text(f'{i} {"в количестве"} {quant[i]}')

def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.regex('^Финансы'), finance_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Потреб'), discretionary_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Энергетика'), energy_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Здравоохранение'), healthcare_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Промышленность'), industrials_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Материалы'), materials_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Ритэйл'), staples_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Технологии'), technology_handler))
    dp.add_handler(MessageHandler(Filters.regex('^Телеком'), tele_handler))
    dp.add_handler(CommandHandler("tic", tic))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("keyboard", get_keyboard))
    dp.add_handler(CommandHandler("portfolio", portfolio_construct))
    dp.add_handler(CommandHandler("describe", describe))
    dp.add_handler(CommandHandler("price", price_chart))
    dp.add_handler(CommandHandler("budget", user_budget))
    dp.add_handler(CommandHandler("value", value_p))
    dp.add_handler(MessageHandler(Filters.text, collecting_user_data))
   
    logging.info("Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()