import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


"""# Convert Bitcoin historical price data to timestamp format.
"""
df = pd.read_csv('coinbase_historical.csv')
df.Timestamp = df.Timestamp.apply(lambda x: datetime.utcfromtimestamp(x))

start_time = datetime(2019, 1,  1) - relativedelta(years=1)

df[df.Timestamp > start_time].to_csv('data/btc/price.csv')


df_fees = pd.read_csv('data_backtest/ETH_help/fees_total_ETH.csv')
df_counts = pd.read_csv('data_backtest/ETH_help/block_count_ETH.csv')
df_rewards = pd.read_csv('data_backtest/ETH_help/reward_total_ETH.csv')

# convert dates
df_fees['Date(UTC)'] = df_fees['Date(UTC)'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
df_counts['Date(UTC)'] = df_counts['Date(UTC)'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
df_rewards['Date(UTC)'] = df_rewards['Date(UTC)'].apply(lambda x: datetime.strptime(x, '%m/%d/%y'))

df_fees_day = pd.DataFrame()
df_fees_day['date'] = df_fees['Date(UTC)']
df_fees_day['avg_fee'] = (df_fees.Value / df_counts.Value) / 10**18
df_fees_day.to_csv('data_backtest/fees_avg_ETH.csv')

df_rewards_day = pd.DataFrame()
df_rewards_day['date'] = df_rewards['Date(UTC)']
df_rewards_day['avg_reward'] = (df_rewards.Value / df_counts.Value)
df_rewards_day.to_csv('data_backtest/rewards_avg_ETH.csv')
df_rewards
