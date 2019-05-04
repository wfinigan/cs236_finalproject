#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 10:05:23 2019

@author: wassy
"""

from __future__ import division
import numpy as np
import math
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from requests import Session
import requests

from secret import cmc_key, eia_key


currency = 'BTC'
def read_difficulty(currency):
    if currency == 'BTC':
        df = pd.read_csv('data_backtest/difficulty_{}.csv'.format(currency), names=['Date', 'Difficulty'])
    elif currency == 'ETH':
        df = pd.read_csv('data_backtest/difficulty_{}.csv'.format(currency))
        df = df.drop(columns = ['UnixTimeStamp'])
        df = df.rename(index=str, columns={"Date(UTC)": 'Date', "Value": "Difficulty"})
        df['Difficulty'] = df['Difficulty']* 10 **12
    df['Date'] = pd.to_datetime(df['Date'])  
    df = df.loc[(df['Date'] >= '2018-01-01') & (df['Date'] <= '2019-01-01')].copy()

    return df

def converrt_difficulty_to_tera_hash(currency, df):
    if currency == 'BTC':
        df['tera_hashrate'] = df['Difficulty'] / 600 * 2 **32 * 10 ** (-12) 
    if currency == 'ETH':
        df['tera_hashrate'] = (df['Difficulty'] / 12 ) / 10 **12
    return df

def get_total_fees(currency):
    if currency == 'BTC':
        df = pd.read_csv('data_backtest/fees_{}.csv'.format(currency), names=['Date', 'Fees'])
    elif currency == 'ETH':
      return "not implemented"
    df['Date'] = pd.to_datetime(df['Date'])  
    df = df.loc[(df['Date'] >= '2018-01-01') & (df['Date'] <= '2019-01-01')].copy()

    return df

def get_blocks_each_day(currency):
    if currency == 'BTC':
        df = pd.read_csv('data_backtest/supply_{}.csv'.format(currency),names=['Date', 'Supply'])
        df['Date'] = pd.to_datetime(df['Date'])  
        df = df.loc[(df['Date'] >= '2017-12-31') & (df['Date'] <= '2019-01-02')].copy()
        df['Money_Added'] = df['Supply'].diff()
        df['Blocks_Found'] = df['Money_Added']/12.5
        df = df.drop(columns = ['Supply', 'Money_Added'])
        df = df.loc[(df['Date'] >= '2018-01-01') & (df['Date'] <= '2019-01-01')].copy()
    elif currency == 'ETH':
        return "have no implemented ether"
    return df

    