import random
import string
import requests
from bs4 import BeautifulSoup


# __init__
base_url = 'http://www.pro-football-reference.com/'


def get_players():

	players = []
	for letter in string.uppercase:
		url = '{}players/{}'.format(base_url, letter)
		resp = requests.get(url)
		soup = BeautifulSoup(resp.text)
		player_div = soup.find_all('div', {'id':'div_players'})[0]
		player_anchors = player_div.find_all('a', href=True)
		players += [(a['href'], a.get_text()) for a in player_anchors]
	return players


def get_player_page(player_endpoint):

	resp = requests.get(base_url + player_endpoint)
	return resp.text


def get_player_draft(player_page):
	pass


# testing
# players = get_players()
player = '/players/A/AbraJo00.htm'
page = get_player_page(player)
page_soup = BeautifulSoup(page)
draft_para = [p.get_text() for p in page_soup.find_all('p') 
				if 'Draft' in p.get_text()][0]

# get round, pick, and year of draft
rgx = '[0-9]+[a-z]*'
out = re.findall(rgx, draft_para)
draft = {'round':out[0], 'overall_pick':out[1], 'year':out[2]}




