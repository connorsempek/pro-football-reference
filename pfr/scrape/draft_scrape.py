#------------------------------------------------------------------------------
# imports

import sys
import re
import string
import datetime as dt
import requests
from bs4 import BeautifulSoup
import pandas as pd

#------------------------------------------------------------------------------
# functions

def get_draft_data(year):
	'''gets nfl draft data since 
	'''

	url = 'http://www.pro-football-reference.com/years/{}/draft.htm'.format(year)
	resp = requests.get(url)
	page = BeautifulSoup(resp.text)
	tbl = page.find_all('table', {'id':'drafts'})[0]

	draft = []
	rows = tbl.find_all('tr')
	for row in rows:
		if not row.attrs:
			tds = row.find_all('td')
			if tds:
				rd = row.find_all('th')[0].get_text()
				vals = [rd] + [td.get_text() for td in tds]
				endpts = row.find_all('a')[:2]
				endpts = [a.attrs['href'] for a in endpts]
				draft.append(vals + endpts) 

	ths = rows[0].find_all('th')
	val_cols = [th.attrs['data-stat'] for th in ths]
	endpt_cols = ['team_endpoint', 'player_endpoint']

	df = pd.DataFrame(draft)
	df.columns = val_cols + endpt_cols
	df['draft_year'] = year
	df.drop('college_link', axis=1, inplace=True)
	return df


# get draft data sine 1967 (year of NFL/AFLL merger)
if __name__ == '__main__':

	sep = '-' * 51
	print sep
	print '\n'

	# get a dump of all drafts
	start_year = 1967
	end_year = dt.datetime.now().year + 1
	years = range(start_year, end_year, 1)
	n = 1.0 * len(years)
	drafts = []
	for i, year in enumerate(years):
		sys.stdout.write('\r')
		drafts.append(get_draft_data(year))
		sys.stdout.write('{} ({:.2%})'.format(year, (i + 1) / n))
		sys.stdout.flush()
	
	df = pd.concat(drafts)
	df.to_csv('all_drafts_1967_to_present.csv', index=False)

	print '\n'
	print 'Saved data to all_drafts_1967_to_present.csv in working directory.'
	print sep
	print '\n'
