import pandas as pd

import player as plyr


def search_player_by_name(name):
	'''search players by name
	'''

	all_players = pd.read_csv('data/all_players.csv')
	row_mask = all_players['name'].str.replace(' ', '')\
					              .str.lower()\
					              .str.contains(name.replace(' ', ''))
	players = all_players[row_mask]
	
	res = None
	n = players.shape[0]
	if n == 0:
		print 'No records for players with names matching {}.'.format(name)
	elif n == 1:
		res = players
		print 'Found match for {}'.format(players['name'].iloc[0])
	else:
		if n > 25:
			print 'There are {} matches, please refine your search'.format(n)
		else:
			print 'There are multiple matches, see below\n'
			print players[['years_active','name','position']]
	return res


def get_player_by_name(name):
	'''get player.Player object using enpoint value in record from search result
	'''

	res = search_player_by_name(name)
	player = ''
	if res is not None:
		endpoint = res['endpoint'].iloc[0]
		player = plyr.Player(endpoint)
	return player




