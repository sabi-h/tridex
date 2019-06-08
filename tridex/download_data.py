from datetime import datetime
import os

import pandas as pd
from pandas_datareader import DataReader

from globals import index_url_suffix
from utils import lse_to_yahoo, yahoo_symbols, extract_symbol


# Global parameters for DataReader - change if yahoo breaks again
ACCESS_KEY = None
DATA_SOURCE = 'yahoo'
INITIAL_DATE = '2014-01-01'

CURRENT_DATE = datetime.now().strptime

ftse100_symbols = yahoo_symbols('../data/symbols/FTSE 100.txt')
ftse250_symbols = yahoo_symbols('../data/symbols/FTSE 250.txt')


def create_index_symbol_map():
	result = {}
	for index in index_url_suffix.keys():
		index_fp = os.path.join('../data/symbols/', index + '.txt')
		with open(index_fp, 'r') as f:
			for symbol in f.readlines():
				symbol = lse_to_yahoo(symbol.strip())
				if symbol not in result:
					result[symbol] = []
				result[symbol].append(index)
	return result


def download(symbol, output_fp):
	"""
	Downloads data and saves in csv format.
	"""
	df = DataReader(name=symbol, data_source=DATA_SOURCE, start=INITIAL_DATE, access_key=ACCESS_KEY)
	df.to_csv(output_fp)


def download_data(symbols):
	"""
	Time ~80sec
	Note: This function will download all data and replace the existing csv files.
	
	Parameters:
		symbols (list): List of strings where each string is a 
			yahoo stock symbol e.g. ['BARC.L', 'HSBA.L']

	"""
	# Parameters for DataReader
	base_output_dir = '../data/stocks/{}/'
	total_symbols = len(symbols)
	index_map = create_index_symbol_map()

	for i, symbol in enumerate(symbols):
		print('{}/{} >>> {}'.format(i+1, total_symbols, symbol))

		market = index_map.get(symbol, [''])[0]
		if not market:
			print('Warning: {} does not have a market...')
			continue

		output_dir = base_output_dir.format(market)
		if not os.path.exists(output_dir):
			os.makedirs(output_dir)

		output_fp = os.path.join(output_dir, symbol + '.csv')
		download(symbol, output_fp)


def update(csv):
	"""
	Updates csv file. Checks the last date
	in csv files and adds new records until the current date.
	"""
	df = pd.read_csv(csv, index_col='Date')
	df.index = pd.to_datetime(df.index, format='%Y-%m-%d')

	# Get the last date in df and add 1 day
	start_date = df.index[-1] + pd.DateOffset(1)
	
	if start_date.strftime('%Y%m%d') != datetime.now().strftime('%Y%m%d'):
		symbol = extract_symbol(csv)
		try:
			new_data_df = DataReader(name=symbol, data_source=DATA_SOURCE, start=start_date, access_key=ACCESS_KEY)
			df = pd.concat([df, new_data_df], axis=0)
			df.to_csv(csv)
		except Exception as e:
			print('Could not update...')
			print(e)


def update_data(market='all'):
	"""
	Uses update function to update every single
	csv file in FTSE100 and FTSE250 directory.
	"""
	# Name of directories to update
	if market == 'all':
		update_dirs = ['FTSE100', 'FTSE250']
	else:
		update_dirs = [market]

	for _dir in update_dirs:
		dir_path = '../data/stocks/{}'.format(_dir)
		filepaths = ['{}/{}'.format(dir_path, x) for x in os.listdir(dir_path)]
		total = len(filepaths)

		print('Updating {} data...'.format(_dir))

		for i, csv in enumerate(filepaths):
			print('{}/{} >>> {}'.format(i+1, total, extract_symbol(csv)))
			update(csv)

def main():
	print('main...')
	download_data(ftse100_symbols)
	download_data(ftse250_symbols)
	# update_data(market='FTSE250')


if __name__ == '__main__':
	main()









