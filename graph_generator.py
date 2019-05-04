#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May  4 10:05:33 2019

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


#graph for project
df = get_history_df('BTC')
df = df[df.shape[0]-365:].copy()
df = df.reset_index()

max_curr = 0
old = df.loc[0]['Adj Close'].copy()
track = list()
for z in range(1,df.shape[0]):
    temp = df.loc[z]['Adj Close'].copy()
    change = (temp - old )/old
    track.append( change)
    old = temp

plt.hist(track *100)
plt.xlabel("Percent Return")
plt.ylabel("Count")
plt.title("Histogram of Bitcoin Close to Close Returns")
plt.show()

