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



def get_price_btc():
    #make this dynamic
    price = 5232.84
    return(price)
    
def get_block_reward():
    #make this dynamic
    block_reward = 12.5 
    return(block_reward)
    
def get_fees():
    #make this dynamic
    fees = 0 
    return(fees)

def get_hashrate():
    #make this dynamic
    #in Giga Hashes
    hashrate = 45867201622
    return(hashrate)
    
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
    return(0.148/(3.6 * 10**6))

def get_Mhash_second():
#make this dynamic
    return(14000000)
 
def get_share_mining():
    hashrate = get_hashrate()
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

#input
#what state you live in (for electricity costs)
#what hardware you use (electricity costs and hash power)