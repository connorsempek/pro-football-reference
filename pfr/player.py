###############################################################################
# Code for getting/parsing/formatting individual player data
#
#------------------------------------------------------------------------------
# TODO: 
#
#	* Get individual-play-level data
#   
###############################################################################


#------------------------------------------------------------------------------
# imports

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import get_tables as tbls

#------------------------------------------------------------------------------
# Player class

class Player(object):


	def __init__(self, player_endpoint):

		self.base = 'http://www.pro-football-reference.com/'
		self.player_endpoint = player_endpoint 
		self.url = self.base + self.player_endpoint 

		self.page = self._get_page()
		self.bio = self._get_bio()

		self.paths = {
			'home'       : '/', 
			'gamelog'    : '/gamelog', 
			'splits'     : '/splits', 
			'penalties'  : '/penalties', 
			'touchdowns' : '/touchdowns',
			}


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
		birth_city = txt['Born'].split('in')[-1].split(',')[0].strip()
		birth_state = txt['Born'].split('in')[-1].split(',')[-1].strip()

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


	def get_path_tables(self, path):
		'''method to get all tables for some path to a player page
		'''

		path_url = self.url.replace('.htm', path)
		resp = requests.get(path_url)
		page = BeautifulSoup(resp.text)
		return tbls.get_stats_tables(page)


	def get_gamelog(self):
		'''gets gamelog data for player
		'''

		path = self.paths['gamelog']
		self.gamelog = self.get_path_tables(path)
	

	def get_penalties(self):		
		'''gets penalty data for player
		'''

		path = self.paths['penalties']
		self.penalties = self.get_path_tables(path)


	def get_splits(self):		
		'''gets split data for player
		'''
		
		path = self.paths['splits']
		self.splits = self.get_path_tables(path)


	def get_touchdowns(self):
		'''gets touchdown data for player
		'''
		path = self.paths['touchdowns']
		self.tds = self.get_path_tables(path)


	def get_play_paths(self):

		div = self.page.find_all('div', {'id':'inner_nav'})[0]
		anchors = div.find_all('a', href=True)
		paths = list(set([a['href'] for a in anchors]))
		return [p for p in paths if 'plays' in p] 


	def get_plays(self):
		
		paths = self.get_play_paths()
		paths = ['/' + '/'.join(p.split('/')[4:]) for p in paths]
		plays = []
		for path in paths:
			year = path.split('/')[-2]
			play_dict = self.get_path_tables(path)
			for k, df in play_dict.items():
				df['year'] = year
			plays.append(play_dict)
		plays = {key: pd.concat([play_dict[key] for play_dict in plays]) 
			for key in plays[0].keys()}
		return plays



if __name__ == '__main__':

	from player import *
	import pandas as pd

	hyde = Player('/players/H/HydeCa00.htm')
	paths = hyde.get_play_paths()
	hyde_plays = hyde.get_plays()['all_plays']

	kaep = Player('/players/K/KaepCo00.htm')
	paths = kaep.get_play_paths()
	kaep_plays = kaep.get_plays()['all_plays']

	bowman = Player('/players/B/BowmNa99.htm')
	paths = bowman.get_play_paths()
	bowman_plays = bowman.get_plays()['all_plays']




