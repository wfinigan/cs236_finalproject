import pandas as pd
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

def clean_dates(df):
    df.date = df.date.apply(lambda x: parser.parse(x))
    df = df[(df.date < end_time) & (df.date >= start_time)]

    return df

"""# Convert Bitcoin historical price data to timestamp format.
"""
df = pd.read_csv('coinbase_historical.csv')
df.Timestamp = df.Timestamp.apply(lambda x: datetime.utcfromtimestamp(x))

end_time = datetime(2019, 1,  1)
start_time = end_time - relativedelta(years=1)

df[df.Timestamp > start_time].to_csv('data/btc/price.csv')


"""# Get average fees per day for ETH.
"""
df_fees_eth = pd.read_csv('data_historical/helper/eth/fees_raw.csv')
df_counts_eth = pd.read_csv('data_historical/helper/eth/block_count.csv')

# convert dates
df_fees_eth['Date(UTC)'] = df_fees['Date(UTC)'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
df_counts_eth['Date(UTC)'] = df_counts['Date(UTC)'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))

df_fees_day_eth = pd.DataFrame()
df_fees_day_eth['date'] = df_fees['Date(UTC)']
df_fees_day_eth['avg_fee'] = (df_fees.Value / df_counts.Value) / 10**18
df_fees_day_eth.to_csv('data_historical/eth/fees.csv')

"""Get bitcoin block count file from total supply change.
"""
df_supply = pd.read_csv('data_historical/helper/btc/supply.csv', names=['date', 'supply'])

df_supply['money_added'] = df_supply['supply'].diff()
df_supply = clean_dates(df_supply)

df_counts_btc = pd.DataFrame()
df_counts_btc['date'] = df_supply.date
df_counts_btc['counts'] = df_supply.money_added / 12.5
df_counts_btc.counts = df_counts_btc.counts.astype(int)
df_counts_btc.to_csv('data_historical/helper/btc/block_count.csv', index=False)

"""# Clean up BTC fees file.
"""
df_fees_btc = pd.read_csv('data_historical/helper/btc/fees_raw.csv', names=['date', 'avg_fees'])
df_fees_btc = clean_dates(df_fees_btc)

df_fees_btc = df_fees_btc.reset_index(drop=True)

df_counts_btc = pd.read_csv('data_historical/helper/btc/block_count.csv')
df_fees_btc.avg_fees = df_fees_btc.avg_fees / df_counts_btc.counts

df_fees_btc.to_csv('data_historical/btc/fees.csv')


"""# Clean up BTC price file.
"""
df_price_btc_raw = pd.read_csv('data_historical/helper/btc/price_raw.csv', index_col=0)
df_price_btc = pd.DataFrame()

df_price_btc['date'] = df_price_btc_raw.Timestamp
df_price_btc['price'] = df_price_btc_raw.Open
df_price_btc.head()

df_price_btc.date = df_price_btc.date.astype(df_fees_btc.date.dtype)
df_price_btc = df_price_btc[(df_price_btc.date >= start_time) & (df_price_btc.date < end_time)]
df_price_btc = df_price_btc.reset_index(drop=True)
df_price_btc.to_csv('data_historical/btc/price.csv')

"""# Clean up ETC price file.
"""
df_price_eth_raw = pd.read_csv('data_historical/helper/eth/price_raw.csv')
df_price_eth_raw.head()

df_price_eth = pd.DataFrame()
df_price_eth['date'] = df_price_eth_raw['Date(UTC)'].astype(df_fees_btc.date.dtype)
df_price_eth = df_price_eth[(df_price_eth.date >= start_time) & (df_price_eth.date < end_time)]

df_price_eth['price'] = df_price_eth_raw.Value
df_price_eth = df_price_eth.reset_index(drop=True)
df_price_eth.to_csv('data_historical/eth/price.csv')
