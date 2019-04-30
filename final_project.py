from __future__ import division
import numpy as np
import math
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from requests import Session
import requests


from secret import cmc_key, eia_key

# coin market cap setup
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': cmc_key,
}

session = Session()
session.headers.update(headers)

def get_prices(coin_ids=['1']):
    """Returns a list of coin get_prices.

    NOTE: Not using this for now -- could be useful when we want to do multiple coins.
    """
    bitcoin_api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {
        'id': ','.join(coin_ids)
    }

    response = session.get(bitcoin_api_url, params=params)
    response_json = response.json()

    prices = []
    for coin_id in coin_ids:
        prices.append(float(response_json['data'][coin_id]['quote']['USD']['price']))

    return(prices)

def get_price_btc():
    return(get_prices(coin_ids=['1'])[0])

def get_block_reward():
    #maybe ke this dynamic
    block_reward = 12.5
    return(block_reward)

def get_fees():
    #make this dynamic
    fees = 0
    return(fees)
    
def get_largest_pct_loss(currency):
    #make currency 'BTC', 'ETH'
    df = pd.read_csv( currency+ '-USD.csv')
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
    return(max_curr)
    
def get_largest_pct_gain(currency):
    #make currency 'BTC', 'ETH'
    df = pd.read_csv( currency+ '-USD.csv')
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
    return(max_curr)
    
def get_avg_pct_change(currency):
        #make currency 'BTC', 'ETH'
    df = pd.read_csv( currency+ '-USD.csv')
    df = df[df.shape[0]-365:].copy()
    df = df.reset_index()
    mylist = list() 
    old = df.loc[0]['Adj Close'].copy()
    for z in range(1,df.shape[0]):
        temp = df.loc[z]['Adj Close'].copy()
        change = (temp - old )/old
        mylist.append(abs(change))
        old = temp
    return(np.average(np.asarray(mylist)))
    
def get_difficulty():
    # get the last published difficulty from when the difficulty was changed TO DO
    difficulty = 6379265451411
    return(difficulty)

def get_blocks_yesterday():
    #get the number of blocks found yesterday TO DO
    blocks_found = 144
    return(blocks_found)

def get_updated_hashrate():
    expected_blocks = 144
    difficulty = get_difficulty()
    blocks_found = get_blocks_yesterday()
    #in tera hashes
    updated_hashrate = (blocks_found/ expected_blocks * difficulty * 2**32 / 600 ) / 10**12
    return(updated_hashrate)

def get_my_hash_rate():
    #make this dynamic
    #assume using the antminer (tera hashes)
    my_hash_rate = 14
    return(my_hash_rate)

def get_Mhash_joule():
    #make this dynamic
    return(10182)

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

def get_share_mining():
    hashrate = get_updated_hashrate()
    my_hash_rate = get_my_hash_rate()
    share_mining = my_hash_rate/ (my_hash_rate + hashrate)
    return(share_mining)

def calculate_costs(state='MA'):
    usd_joule = get_usd_joule()[state]

    Mhash_joule = get_Mhash_joule()
    Mhash_second = get_my_hash_rate() * 10**6
    seconds = 60 * 10
    e_costs = usd_joule / Mhash_joule *Mhash_second  * seconds
    return(e_costs)

def calculate_profit(case, currency):
    block_reward = get_block_reward()
    if case == 'w':
        price = get_price_btc() * (1 + get_largest_pct_loss(currency))
    if case == 'b':
        price = get_price_btc() * (1 + get_largest_pct_gain(currency))
    if case == 'ag':
        price = get_price_btc() *  (1 + get_avg_pct_change(currency))
    if case == 'ab':
        price = get_price_btc()*  (1 - get_avg_pct_change(currency))
    if case == 'na':
        price = get_price_btc()
    fees = get_fees()
    share_mining = get_share_mining()
    USD = price * (block_reward + fees) * share_mining
    return(USD)

def calculate_ev(case,currency):
    #case can be 'w' for worst, 'g' for good, 'ab' for average bad, 'ab' for average bad ,and 'na'
    costs = calculate_costs()
    profit = calculate_profit()
    ev = profit - costs
    return(ev)

#input
#what state you live in (for electricity costs)
#what hardware you use (electricity costs and hash power)
