#все по портфелю

import logging
import pandas as pd
import yfinance as yf
import numpy as np
import redis
import json
import ephem 
import pandas_datareader as web
import matplotlib.pyplot as plt
from pypfopt.expected_returns import mean_historical_return
from pypfopt import risk_models 
from pypfopt import expected_returns
from pypfopt.cla import CLA
import pypfopt.plotting as pplt
from matplotlib.ticker import FuncFormatter
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
import finance

def portfolio_construct (list, date):
    time_shares = yf.download(list, start = date - timedata(days=365), end=date) ['Adj Close']
    mu = mean_historical_return(time_shares)
    S = CovarianceShrinkage(time_shares).ledoit_wolf()
    ef = EfficientFrontier(mu, S, weight_bounds = (0,1))
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    update.message.reply_text(cleaned_weights)

def my_budget_portfolio (update, context, message):
    bot.send_message(message.chat.id, 'Введите сумму')
    sum = message.text()
    latest_prices = get_latest_prices(time_shares)
    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value = sum)
    allocation, leftover = da.lp_portfolio()
    bot.send_message(message.chat.id, f' Потратив {sum}, вы сможете купить такое количество акций от каждой компании в эффективном портфеле: {allocation}')

def my_portfolio_stat (update, context, message):
    update.message.reply_text(ef.portfolio_performance(verbose=True))

def my_portfolio_chart (update, context, message):
    cl_obj = CLA(mu, S)
    ax = pplt.plot_efficient_frontier(cl_obj, showfig = False)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: '{:.0%}'.format(x)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
    fig1, ax1 = plt.subplots()
    ax1.pie(t_weights, labels=tickers)
    ax1.axis('equal')
    patches, texts, auto = ax1.pie(t_weights, startangle=90, autopct='%1.1f%%' )
    plt.legend(patches, tickers, loc="best")
    bot.message.reply_text(ax, plt.show())