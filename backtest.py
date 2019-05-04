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
import datetime
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


def get_difficulty(currency, timestamp):
    if currency == 'BTC':
        df = read_difficulty('BTC')
        diff = df[df['Date'] ==pd.Timestamp(timestamp.date())]['Difficulty'].copy()
        diff = list(diff)[0]
    elif currency == 'ETH':
        # just use most recent diff
        diff = int(ethereum_data[0]['difficulty'])

    else:
        raise ValueError('Currency {} not yet implemented.'.format(currency))

    return diff


def get_avg_fee(currency):
    if currency == 'BTC':
        df = pd.read_csv('data_backtest/fees_{}.csv'.format(currency), names=['Date', 'Fees'])
        df['Date'] = pd.to_datetime(df['Date'])  
        df = df.loc[(df['Date'] >= '2018-01-01') & (df['Date'] <= '2019-01-01')].copy()
        blocks = get_blocks_each_day(currency)
        df = pd.concat([df, blocks], axis=1)
        df['Fee_Block'] = df['Fees']/ df['Blocks_Found']
        df = df[['Date', "Fee_Block"]].copy()
        df = df.loc[:,~df.columns.duplicated()].copy()
    elif currency == 'ETH':
      return "not implemented"

    return df

def get_fees(currency, timestamp):
    if currency == 'BTC':
        df = get_avg_fee(currency)
        fees = df[df['Date'] ==pd.Timestamp(timestamp.date())]['Fee_Block'].copy()
        fees = list(fees)[0]

    elif currency == 'ETH':
        gas_total = 0
        for block in ethereum_data:
            gas_total += float(block['fee_total'])

        # get average fees per block
        fees_gw = gas_total / len(ethereum_data)

        # wei to ether
        fees = fees_gw / 10**18

    else:
        raise ValueError('Currency {} not yet implemented.'.format(currency))

    return fees

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

def get_blocks_yesterday(currency, timestamp):
    df = get_blocks_each_day(currency)
    blocks_yesterday = df[df['Date'] ==pd.Timestamp(timestamp.date())]['Blocks_Found'].copy()
    blocks_yesterday = list(blocks_yesterday)[0]
    return blocks_yesterday
 
def get_price(currency, timestamp): 
    if currency == 'BTC':
        df = pd.read_csv('price_historical_year.csv')
        df = df[["Timestamp", "Open"]].copy()
        df = df.loc[(df['Timestamp'] >= '2018-01-01') & (df['Timestamp'] <= '2019-01-01')].copy()
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        price = list(df[df['Timestamp'] == timestamp]['Open'])[0]
    return price



def get_block_reward(currency):
    if currency == 'BTC':
        block_reward = 12.5
    elif currency == 'ETH':
        block_reward = 2

    return block_reward




def get_history_df(currency):
    try:
        df = pd.read_csv('{}-USD.csv'.format(currency))
    except IOError:
        raise ValueError('No history file found for currency {}'.format(currency))

    return df


def get_largest_pct_loss(currency):
    df = get_history_df(currency)
    df = df[df.shape[0]-365:].copy()
    df = df.reset_index()

    max_curr = 0
    old = df.loc[0]['Adj Close'].copy()

    for z in range(1,df.shape[0]):
        temp = df.loc[z]['Adj Close'].copy()
        change = (temp - old )/old
        if change <  max_curr:
            max_curr = change
        old = temp

    return max_curr


def get_largest_pct_gain(currency):
    df = get_history_df(currency)
    df = df[df.shape[0]-365:].copy()
    df = df.reset_index()

    max_curr = 0
    old = df.loc[0]['Adj Close'].copy()

    for z in range(1,df.shape[0]):
        temp = df.loc[z]['Adj Close'].copy()
        change = (temp - old )/old
        if change > max_curr:
            max_curr = change
        old = temp

    return max_curr


def get_avg_pct_change(currency):
    df = get_history_df(currency)
    df = df[df.shape[0]-365:].copy()
    df = df.reset_index()

    mylist = list()
    old = df.loc[0]['Adj Close'].copy()

    for z in range(1,df.shape[0]):
        temp = df.loc[z]['Adj Close'].copy()
        change = (temp - old )/old
        mylist.append(abs(change))
        old = temp

    return np.average(np.asarray(mylist))





def get_updated_hashrate(currency, timestamp):
    difficulty = get_difficulty(currency, timestamp)
    if currency == 'BTC':
        expected_blocks = 144
        blocks_found = get_blocks_yesterday(currency, timestamp)
        #in tera hashes
        updated_hashrate = (blocks_found / expected_blocks * difficulty * 2**32 / 600 ) / 10**12
    elif currency == 'ETH':
        updated_hashrate = ( difficulty  / 12 ) / 10**12

    return updated_hashrate


def get_my_hash_rate(currency):
    if currency == 'BTC':
    # using antminer (tera hashes)
        my_hash_rate = 14

    if currency == 'ETH':
        # 33 MH convert to TeraHashes
        my_hash_rate = 33 * 10 **-6

    return my_hash_rate


def get_Mhash_joule(currency):
    if currency == 'BTC':
        return 10182

    if currency == 'ETH':
        #MHash per second divided by watts
        return 33 / 200


def get_usd_joule():
    """Return dictionary mapping State IDs to dollars per joule average price in previous month.
    """
    url = 'http://api.eia.gov/category/'
    params = {
        'api_key': eia_key,
        'category_id': '40'
    }
    response = requests.get(url, params=params)
    response_json = response.json()

    series_ids = []
    for child in response_json['category']['childseries']:
        tokens = child['series_id'].split('.')

        if tokens[-1] == 'M':
            state = tokens[-2].split('-')[0]
            if len(state) == 2 and state != "US":
                series_ids.append(child['series_id'])

    states = {}
    for series_id in series_ids:
        url = 'http://api.eia.gov/series/'
        params = {
            'api_key': eia_key,
            'series_id': series_id,
        }
        response = requests.get(url, params=params)
        response_json = response.json()

        # get state name
        state = response_json['series'][0]['geography'].split('-')[1]

        # convert to dollars per joule
        cost = response_json['series'][0]['data'][0][1] / (100 * (3.6 * 10**6))
        states[state] = cost

    return states


def get_share_mining(currency, timestamp):
    hashrate = get_updated_hashrate(currency,timestamp)
    my_hash_rate = get_my_hash_rate(currency)
    share_mining = my_hash_rate/ (my_hash_rate + hashrate)

    return share_mining


def calculate_costs(currency, state='MA'):
    usd_joule = get_usd_joule()[state]
    Mhash_joule = get_Mhash_joule(currency)
    Mhash_second = get_my_hash_rate(currency) * 10**6
    if currency == 'BTC':
        seconds = 60 * 10
    if currency == 'ETH':
    #expected time to mine a block is 12 seconds
        seconds = 12
    e_costs = usd_joule / Mhash_joule *Mhash_second  * seconds

    return e_costs


def calculate_profit(case, currency, timestamp):
    block_reward = get_block_reward(currency)
    if case == 'w':
        price = get_price(currency) * (1 + get_largest_pct_loss(currency))
    if case == 'b':
        price = get_price(currency) * (1 + get_largest_pct_gain(currency))
    if case == 'ag':
        price = get_price(currency) *  (1 + get_avg_pct_change(currency))
    if case == 'ab':
        price = get_price(currency)*  (1 - get_avg_pct_change(currency))
    if case == 'na':
        price = get_price(currency, timestamp)

    fees = get_fees(currency,timestamp)
    share_mining = get_share_mining(currency, timestamp)
    USD = price * (block_reward + fees) * share_mining

    return USD


def calculate_ev(case, currency, timestamp, state='MA'):
    #case can be 'w' for worst, 'g' for good, 'ab' for average bad, 'ab' for average bad ,and 'na'
    costs = calculate_costs(currency, state=state)
    profit = calculate_profit(case, currency, timestamp)
    if currency == 'BTC':
        seconds = 600
    elif currency == 'ETH':
        seconds = 12
    ev = (profit - costs)/seconds

    return ev

# store as global
ethereum_data = get_ethereum_data()


def what_to_do(case, state, timestamp):
    btc_ev = calculate_ev(case, 'BTC', state)
    ether_ev = calculate_ev(case, 'ETH', state)
    decision = max(btc_ev, ether_ev, 0)
    if decision == btc_ev:
        text = "BTC"
    elif decision== ether_ev:
        text = "ETH"
    else:
        text = "NA"
    return([decision, text])

what_to_do('na', state = 'MA')
what_to_do('na', state = 'OK')
what_to_do('b', state = 'OK')

def run_backtest():
    df = pd.read_csv('price_historical_year.csv')
    df = df[["Timestamp"]].copy()
    df = df.loc[(df['Timestamp'] >= '2018-01-01') & (df['Timestamp'] <= '2019-01-01')].copy()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['EV'] = 0 
    for i in range(len(df)):
        timestamp = df.iloc[i][0]
        print(timestamp)
        print calculate_ev('na', 'BTC',timestamp,state='MA')

run_backtest()
    