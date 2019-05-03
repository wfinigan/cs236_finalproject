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

def get_ethereum_data():
    headers = {
        'x-api-key': 'UAK2176517602aef96e2ac77f16e7479153'
    }

    response = requests.get('https://web3api.io/api/v1/blocks', headers=headers)
    response_json = response.json()

    return response_json['payload']


def get_price(currency):
    coind_id_map = {
        'BTC': '1',
        'ETH': '2',
    }

    coin_id = coind_id_map[currency]

    bitcoin_api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    params = {
        'id': coin_id
    }

    response = session.get(bitcoin_api_url, params=params)
    response_json = response.json()

    return float(response_json['data'][coin_id]['quote']['USD']['price'])


def get_block_reward(currency):
    if currency == 'BTC':
        block_reward = 12.5
    elif currency == 'ETH':
        block_reward = 2

    return block_reward


def get_fees(currency, days=1):
    if currency == 'BTC':
        url = 'https://api.smartbit.com.au/v1/blockchain/stats'
        response = requests.get(url, params={'days': days})
        response_json = response.json()

        fees = float(response_json['stats']['fees']) / int(response_json['stats']['block_count'])

    elif currency == 'ETH':
        gas_total = 0
        for block in ethereum_data['payload']:
            gas_total += float(block['gasUsed'])

        # get average fees per block
        fees_gw = gas_total / len(ethereum_data['payload'])

        # gigawei to wei
        fees = fees_gw / 10**9

    else:
        raise ValueError('Currency {} not yet implemented.'.format(currency))

    return fees


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


def get_difficulty(currency):
    if currency == 'BTC':
        url = 'https://api.smartbit.com.au/v1/blockchain/stats'
        response = requests.get(url)
        response_json = response.json()

        diff = float(response_json['stats']['end_difficulty'])
    elif currency == 'ETH':
        # just use most recent diff
        diff = int(ethereum_data['payload'][-1]['difficulty'])

    else:
        raise ValueError('Currency {} not yet implemented.'.format(currency))

    return diff


def get_blocks_yesterday():
    url = 'https://api.smartbit.com.au/v1/blockchain/stats'
    response = requests.get(url)
    response_json = response.json()

    return response_json['stats']['block_count']


def get_updated_hashrate(currency):
    if currency == 'BTC':
        expected_blocks = 144
        difficulty = get_difficulty(currency)
        blocks_found = get_blocks_yesterday()
        #in tera hashes
        updated_hashrate = (blocks_found / expected_blocks * difficulty * 2**32 / 600 ) / 10**12
    elif currency == 'ETH':
        raise ValueError('Ethereum not yet implemented.')

    return updated_hashrate


def get_my_hash_rate(currency):
    if currency == 'BTC':
    # using antminer (tera hashes)
        my_hash_rate = 14

    if currency == 'ETH':
        # 33 MH
        my_hash_rate = 0.033

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


def get_share_mining(currency):
    hashrate = get_updated_hashrate(currency)
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
    #expected time to mine a block is 17 seconds
        seconds = 12
    e_costs = usd_joule / Mhash_joule *Mhash_second  * seconds

    return e_costs


def calculate_profit(case, currency):
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
        price = get_price(currency)

    fees = get_fees(currency)
    share_mining = get_share_mining(currency)
    USD = price * (block_reward + fees) * share_mining

    return USD


def calculate_ev(case, currency, state='MA'):
    #case can be 'w' for worst, 'g' for good, 'ab' for average bad, 'ab' for average bad ,and 'na'
    costs = calculate_costs(currency, state=state)
    profit = calculate_profit(case, currency)
    ev = profit - costs

    return ev

# store as global
ethereum_data = get_ethereum_data()

calculate_ev('w', 'ETH', state='OK')
calculate_ev('na', 'BTC', state='MA')
