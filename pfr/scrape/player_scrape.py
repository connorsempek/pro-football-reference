#------------------------------------------------------------------------------
# imports

import sys
import re
import string
import requests
from bs4 import BeautifulSoup
import pandas as pd


#------------------------------------------------------------------------------
# functions

def get_players(letter):
	'''gets a list of players whose last names begin with letter
	'''

	url = 'http://www.pro-football-reference.com/players/{}'.format(letter)
	resp = requests.get(url)
	page = BeautifulSoup(resp.text)
	div = page.find_all('div', {'id':'div_players'})[0]
	paras = div.find_all('p') 

	# parse out data
	n = len(paras)
	players = []
	for i, p in enumerate(paras):	
		player = {}
		anchor = p.find_next('a') 
		player['name'] = anchor.get_text()
		player['endpoint'] = anchor.attrs.values()[0]
		player['is_active'] = p.findChild().name == 'b' # bold = active
		player['position'] = p.get_text().split('(')[-1].split(')')[0]
		player['years_active'] = re.findall('[0-9]{4}-[0-9]{4}', p.get_text())[0]
		players.append(player)
	return players


# get a list of all players and their pfr endpoints and save to csv
if __name__ == '__main__':

	sep = '-' * 51
	print sep
	print '\n'

	# get a dump of all players
	all_players = []
	for i, letter in enumerate(string.uppercase):
		sys.stdout.write('\r')
		all_players += get_players(letter)
		sys.stdout.write('{} ({:.2%})'.format(letter, (i+1) / 26.0))
		sys.stdout.flush()
	
	df = pd.DataFrame(all_players)
	df.to_csv('all_players.csv', index=False)

	print '\n'
	print 'Saved data to all_players.csv in working directory.'
	print sep
	print '\n'
