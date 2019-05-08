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
    response = requests.get('https://api.blockchair.com/ethereum/blocks')
    response_json = response.json()

    return response_json['data']


def get_price(currency, timestamp_data):
    if timestamp_data is None:
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
    else:
        return timestamp_data[currency.lower()]['price']


def get_block_reward(currency, timestamp_data):
    block_reward_data = {
        'BTC': {
            None: 12.5,
            2018: 12.5
        },
        'ETH': {
            None: 3,
            2018: 2
        }
    }

    if timestamp_data is None:
        return block_reward_data[currency][timestamp_data]
    else:
        return block_reward_data[currency][2018]


def get_fees(currency, timestamp_data, days=1):
    if timestamp_data is None:
        if currency == 'BTC':
            url = 'https://api.smartbit.com.au/v1/blockchain/stats'
            response = requests.get(url, params={'days': days})
            response_json = response.json()

            fees = float(response_json['stats']['fees']) / int(response_json['stats']['block_count'])

        elif currency == 'ETH':
            gas_total = 0
            for block in ethereum_data_now:
                gas_total += float(block['fee_total'])

            # get average fees per block
            fees_gw = gas_total / len(ethereum_data_now)

            # wei to ether
            fees = fees_gw / 10**18

        else:
            raise ValueError('Currency {} not yet implemented.'.format(currency))
    else:
        fees = timestamp_data[currency.lower()]['fees'] / timestamp_data[currency.lower()]['counts']

    return fees


def get_difficulty(currency, timestamp_data):
    if timestamp_data is None:
        if currency == 'BTC':
            url = 'https://api.smartbit.com.au/v1/blockchain/stats'
            response = requests.get(url)
            response_json = response.json()

            diff = float(response_json['stats']['end_difficulty'])
        elif currency == 'ETH':
            # just use most recent diff
            diff = int(ethereum_data_now[0]['difficulty'])

        else:
            raise ValueError('Currency {} not yet implemented.'.format(currency))
    else:
        diff = timestamp_data[currency.lower()]['diff']

    return diff


def get_blocks_yesterday(currency, timestamp_data):
    if timestamp_data is None:
        if currency == 'BTC':
            url = 'https://api.smartbit.com.au/v1/blockchain/stats'
            response = requests.get(url)
            response_json = response.json()

            return response_json['stats']['block_count']
        else:
            raise ValueError('Currency {} not yet implemented.'.format(currency))
    else:
        return timestamp_data[currency.lower()]['counts']




def get_updated_hashrate(currency, timestamp_data):
    difficulty = get_difficulty(currency, timestamp_data)
    if currency == 'BTC':
        expected_blocks = 144
        blocks_found = get_blocks_yesterday(currency, timestamp_data)
        #in tera hashes
        updated_hashrate = (blocks_found / expected_blocks * difficulty * 2**32 / 600 ) / 10**12
    elif currency == 'ETH':
        updated_hashrate = (difficulty  / 12 ) / 10**12

    return updated_hashrate


def get_my_hash_rate(currency):
    """TODO: Change to historical?
    """
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

def get_usd_joule(timestamp_data):
    """Return dictionary mapping State IDs to dollars per joule average price in previous month.
    """
    if timestamp_data is None:
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
    else:
        states = timestamp_data['elec']

    return states


def get_history_df(currency):
    try:
        df = pd.read_csv('data/{}/ohlc.csv'.format(currency))
    except IOError:
        raise ValueError('No history file found for currency {}'.format(currency))
    return df


def get_largest_pct_loss(currency):
    df = get_history_df(currency)
    df = df[df.shape[0]-365:].copy()
    df = df.reset_index()

    max_curr = 0
    old = df.loc[0]['adj_close'].copy()

    for z in range(1,df.shape[0]):
        temp = df.loc[z]['adj_close'].copy()
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
    old = df.loc[0]['adj_close'].copy()

    for z in range(1,df.shape[0]):
        temp = df.loc[z]['adj_close'].copy()
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
    old = df.loc[0]['adj_close'].copy()

    for z in range(1,df.shape[0]):
        temp = df.loc[z]['adj_close'].copy()
        change = (temp - old )/old
        mylist.append(abs(change))
        old = temp

    return np.average(np.asarray(mylist))


def get_share_mining(currency, timestamp_data):
    hashrate = get_updated_hashrate(currency, timestamp_data)
    my_hash_rate = get_my_hash_rate(currency)
    share_mining = my_hash_rate/ (my_hash_rate + hashrate)

    return share_mining


def calculate_costs(currency, state, timestamp_data):
    usd_joule = get_usd_joule(timestamp_data)[state]
    Mhash_joule = get_Mhash_joule(currency)
    Mhash_second = get_my_hash_rate(currency) * 10**6
    if currency == 'BTC':
        seconds = 60 * 10
    if currency == 'ETH':
    #expected time to mine a block is 12 seconds
        seconds = 12
    e_costs = usd_joule / Mhash_joule * Mhash_second * seconds

    return e_costs


def calculate_profit(case, currency, timestamp_data, data=None):
    curr = currency.lower()

    if data is None:
        data = {curr: {}}
        data[curr]['largest_pct_loss'] = get_largest_pct_loss(curr)
        data[curr]['largest_pct_gain'] = get_largest_pct_gain(curr)
        data[curr]['avg_pct_change'] = get_avg_pct_change(curr)

    block_reward = get_block_reward(currency, timestamp_data)
    if case == 'w':
        price = get_price(currency, timestamp_data) * (1 + data[curr][largest_pct_loss])
    if case == 'b':
        price = get_price(currency, timestamp_data) * (1 + data[curr][largest_pct_gain])
    if case == 'ag':
        price = get_price(currency, timestamp_data) *  (1 + data[curr][avg_pct_change])
    if case == 'ab':
        price = get_price(currency, timestamp_data) *  (1 - data[curr][avg_pct_change])
    if case == 'na':
        price = get_price(currency, timestamp_data)

    fees = get_fees(currency, timestamp_data)
    share_mining = get_share_mining(currency, timestamp_data)
    USD = price * (block_reward + fees) * share_mining

    return USD


def calculate_ev(case, currency, state, timestamp_data, data=None):
    #case can be 'w' for worst, 'g' for good, 'ab' for average bad, 'ab' for average bad ,and 'na'
    costs = calculate_costs(currency, state, timestamp_data)
    profit = calculate_profit(case, currency, timestamp_data, data=data)

    if currency == 'BTC':
        seconds = 600
    elif currency == 'ETH':
        seconds = 12
    ev = (profit - costs) / seconds

    return ev

# store as global
ethereum_data_now = get_ethereum_data()


def get_ohlc_data():
    ohlc_data = {'eth': {}, 'btc': {}}
    for curr in ohlc_data:
        ohlc_data[curr]['largest_pct_loss'] = get_largest_pct_loss(curr)
        ohlc_data[curr]['largest_pct_gain'] = get_largest_pct_gain(curr)
        ohlc_data[curr]['avg_pct_change'] = get_avg_pct_change(curr)

    return ohlc_data


def what_to_do(case, state, timestamp_data, data=None):
    """Get up to date information on what to do given a timestamp_data or timestamp_data=None for now.
    """
    btc_ev = calculate_ev(case, 'BTC', state, timestamp_data, data=data)
    ether_ev = calculate_ev(case, 'ETH', state, timestamp_data, data=data)
    decision = max(btc_ev, ether_ev, 0)
    if decision == btc_ev:
        text = "BTC"
    elif decision== ether_ev:
        text = "ETH"
    else:
        text = "NA"
    return([decision, text])


def set_dt_index(df):
    df = df.set_index(pd.DatetimeIndex(df.date))
    return df.drop(columns=['date'])


def run_backtest(method, state):

    ohlc_data = get_ohlc_data()
    currs = ['eth', 'btc']

    output_dict = {'date': []}
    data_sets = {}
    for curr in currs:
        data_sets[curr] = {}
        output_dict[curr] = []

    types = ['fees', 'price', 'diff', 'counts']

    elec_data = set_dt_index(pd.read_csv('data/elec_data.csv', index_col=0))
    data_sets['elec'] = elec_data[elec_data.state == state]

    for curr in currs:
        for type in types:
            data_sets[curr][type] = set_dt_index(pd.read_csv('data/{}/{}.csv'.format(curr, type), index_col=0))
    counter = 0
    for ts in data_sets['btc']['price'].index:
        if counter % 10000 == 0:
            ts_data = {
                'eth': {},
                'btc': {},
            }
            e_i = data_sets['elec'].index.get_loc(ts, method='nearest')
            ts_data['elec'] = {state: data_sets['elec'].price[e_i]}

            for curr in currs:
                for type in types:
                    index = data_sets[curr][type].index.get_loc(ts, method='nearest')
                    ts_data[curr][type] = data_sets[curr][type][type][index]

            btc_ev = calculate_ev(method, 'BTC', state, ts_data, data=ohlc_data)
            eth_ev = calculate_ev(method, 'ETH', state, ts_data, data=ohlc_data)

            output_dict['btc'].append(btc_ev)
            output_dict['eth'].append(eth_ev)
            output_dict['date'].append(ts)

        counter +=1

    return pd.DataFrame(output_dict)
