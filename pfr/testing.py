import random
import string
import requests
from bs4 import BeautifulSoup

import player

# for testing Player class
player_endpoint = 'players/H/HydeCa00.htm'
p = player.Player(player_endpoint)

# print bio info of player
print '\n'
s = '{} plays for the {}. He stands {} tall and weighs in at {}'
print s.format(p.bio['name'], p.bio['team'], p.bio['height'], p.bio['weight'])

# get gamelog
gl = p.get_gamelog()
print '\n'
print 'Total Rushing Yards'
print gl.groupby('year').rush_yds.sum()
