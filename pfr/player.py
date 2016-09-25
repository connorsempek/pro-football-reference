###############################################################################
# Code for getting/parsing/formatting individual player data
#
#------------------------------------------------------------------------------
# TODO: 
#
#	1. Add methods for 
#   
###############################################################################


#------------------------------------------------------------------------------
# imports

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

#------------------------------------------------------------------------------
# Player class

class Player(object):


	def __init__(self, player_endpoint):

		self.base = 'http://www.pro-football-reference.com/'
		self.player_endpoint = player_endpoint 
		self.url = self.base + self.player_endpoint 

		self.page = self._get_page()
		self.bio = self._get_bio() # leave out?

		# columns for gamelog data
		self.gamelog_columns = [
			'year', 'date', 'game', 'age', 'team', 'opp', 'result', 'rush', 
			'rush_yds', 'yds_per_rush', 'rush_tds', 'rec_tgt', 'rec', 
			'rec_yds', 'yds_per_rec', 'rec_tds', 'rec_pct', 'yds_per_tgt',
			'ret', 'ret_yds', 'yds_per_ret', 'ret_tds', 'tds', 'points'
			]


	def _get_page(self):

		resp = requests.get(self.url)
		return BeautifulSoup(resp.text)


	def _get_bio(self):

		# get div containing biographical blurb
		bio = self.page.find_all(
			'div', 
			{'itemtype': 'http://schema.org/Person'}
			)[0]

		# easily parsed tagged data
		name = bio.find_all('h1', {'itemprop': 'name'})[0].get_text()
		height = bio.find_all('span', {'itemprop': 'height'})[0].get_text()
		weight = bio.find_all('span', {'itemprop': 'weight'})[0].get_text()
		team = bio.find_all('span', {'itemprop': 'affiliation'})[0].get_text()

		# text containing untagged data points
		pars = [p.get_text() for p in bio.find_all('p') if ':' in p.get_text()]
		par_splits = [s.split(':') for s in pars]
		txt = {s[0].strip(): s[1].strip() for s in par_splits}

		# position (current)
		position = txt['Position']

		# player birth time and place
		dob = txt['Born'].split('\n')[0].replace(u'\xa0', u' ')
		birth_state = txt['Born'].split('in')[-1].split(',')[0].strip()
		birth_city = txt['Born'].split('in')[-1].split(',')[-1].strip()

		# NFL draft round, overall pick, and year
		draft = txt['Draft']
		draft_round = re.findall('[0-9]+[a-z]* round', draft)[0].split()[0]
		draft_pick = re.findall('[0-9]+[a-z]* overall', draft)[0].split()[0]
		draft_year = re.findall('[0-9]* NFL Draft.', draft)[0].split()[0]

		# get college
		college = None
		if 'College' in txt.keys():
			college = txt['College'].split('\n')[0].strip()

		# get high school
		hs = None
		if 'High School' in txt.keys():
			hs = txt['High School']

		# format data
		bio_data = {
			'name'        : name,
			'height'      : height,
			'weight'      : weight,
			'team'        : team,
			'position'    : position,
			'dob'         : dob,
			'birth_state' : birth_state,
			'birth_city'  : birth_city,
			'draft_round' : draft_round,
			'draft_pick'  : draft_pick,
			'draft_year'  : draft_year,
			'hs'          : hs,
			'college'     : college,
			}
		return bio_data


	def get_gamelog(self):
		'''gets gamelog data for player
		'''

		resp = requests.get(self.url + '/gamelog')
		page = BeautifulSoup(resp.text)
		tbl = page.find_all('table')[0]
		rows = tbl.find_all('tr')[1:-1]
		gamelog = []
		for row in rows[1:]:
			if row.attrs:
				if row.has_attr('id'):	
					vals = [td.get_text() for td in row.find_all('td')]
					if vals:
						gamelog.append(vals)
		df = pd.DataFrame(gamelog)
		
		# drop axis containing only '@'
		df.drop(5, axis=1, inplace=True)

		# set columns to unique, descriptive names
		df.columns = self.gamelog_columns

		# replace empty strings with 0
		df.replace('', 0, inplace=True)

		# remove percent symbol
		df.loc[:, 'rec_pct'] = df.loc[:, 'rec_pct'].str.replace('%', '')
		
		# make columns that should be numeric numeric
		num_cols = self.gamelog_columns[7:]
		df[num_cols] = df[num_cols].astype(float) 
		return df


	def get_




