# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import numpy as np
import math
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from __future__ import division
import requests


def get_price_btc():
    #price = 5232.84
    bitcoin_api_url = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/'
    response = requests.get(bitcoin_api_url)
    response_json = response.json()
    price = float(response_json[0]['price_usd'])
    return(price)

def get_block_reward():
    #maybe ke this dynamic
    block_reward = 12.5
    return(block_reward)

def get_fees():
    #make this dynamic
    fees = 0
    return(fees)

#def get_hashrate():
#    #make this dynamic
#    #in Giga Hashes
#    hashrate = 45867201622
#    return(hashrate)
    
def get_difficulty():
    # get the last published difficulty from when the difficulty was changed
    difficulty = 
    return(difficulty)

def get_blocks_yesterday():
    #get the number of blocks found yesterday
    blocks_found = 
    return(blocks_found)

def get_updated_hashrate():
    expected_blocks = 144
    difficulty = get_difficulty()
    blocks_found = get_blocks_yesterday()
    #figure out why this is true
    #in giga hashes
    updated_hashrate = (blocks_found/ expected_blocks * difficulty * 2**32 / 600 ) / 10**9
    return(updated_hashrate)
    
def get_my_hash_rate():
    #make this dynamic
    #assume using the antminer (Giga hashes)
    my_hash_rate = 14000
    return(my_hash_rate)

def get_Mhash_joule():
    #make this dynamic
    return(10182)

def get_usd_joule():
#assume in massachusetts
    # price per kwh
    return(0.148/(3.6 * 10**6))

def get_Mhash_second():
#make this dynamic
    return(14000000)

def get_share_mining():
    hashrate = get_updated_hashrate()
    my_hash_rate = get_my_hash_rate()
    share_mining = my_hash_rate/ (my_hash_rate + hashrate)
    return(share_mining)

def calculate_costs():
    usd_joule = get_usd_joule()
    Mhash_joule = get_Mhash_joule()
    Mhash_second = get_Mhash_second()
    seconds = 60 * 10
    e_costs = usd_joule / Mhash_joule *Mhash_second  * seconds
    return(e_costs)

def calculate_profit():
    block_reward = get_block_reward()
    price = get_price_btc()
    fees = get_fees()
    share_mining = get_share_mining()
    USD = price * (block_reward + fees) * share_mining
    return(USD)

def calculate_ev():
    costs = calculate_costs()
    profit = calculate_profit()
    ev = profit - costs
    return(ev)

def get_block_times():
    return None

#input
#what state you live in (for electricity costs)
#what hardware you use (electricity costs and hash power)
