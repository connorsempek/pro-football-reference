# tools for parsing out tables on pfr pages

import re
import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd

########################################################################

def uncomment(comment):
	'''uncomment beautiful soup comment
	'''
	return BeautifulSoup(comment.extract())


def get_comments(page):

	return page.find_all(text=lambda txt: isinstance(txt, Comment))


def get_tables(page, attrs={}):

	return page.find_all('table', attrs=attrs)


def get_commented_tables(page, attrs={}):

	comments = get_comments(page)
	tables = []
	for comment in comments:
		if '<table' in comment:
			tables.append(uncomment(comment))
	return [table.find('table') for table in tables]

	
def get_all_tables(page):
	
	return get_tables(page) + get_commented_tables(page)


def is_stats_table(table):
	'''returns true if table has attribute class="stats_table" where
	table is BeautifulSoup object of form <table ...>...</table>
	'''

	is_stats_table = False
	if table.has_attr('class'):
		is_stats_table = 'stats_table' in table.attrs['class']
	return is_stats_table


def get_table_id(table):

	return table.attrs['id']


def is_data_row(row, table_id):
	'''returns true if row has attribute id="stats.*" where
	row is BeautifulSoup object of form <tr ...>...</tr>
	'''
	is_data_row = False
	if row.has_attr('id'):
		is_data_row = table_id in row.attrs['id']
	# !!! TODO: second condition is gross, clean up
	elif not row.attrs:
		if row.find_all('td'):
			is_data_row = True
	return is_data_row


def get_stats_row_data(row):

	ths = row.find_all('th')
	tds = row.find_all('td')
	data = ths + tds
	return {d.attrs['data-stat']: d.get_text() for d in data}


def get_stats_table_data(table):

	data = []
	table_id = get_table_id(table)
	rows = table.find_all('tr')
	for row in rows:
		if is_data_row(row, table_id):
			data.append(get_stats_row_data(row))
	return pd.DataFrame(data)


def get_stats_tables(page):

	tables = get_all_tables(page)
	stats_tables = [table for table in tables if is_stats_table(table)]
	stats_tables = {get_table_id(table): get_stats_table_data(table)
						for table in stats_tables}
	return stats_tables



#------------------------------------------------------------------------------
# testing

if __name__ == '__main__':

	base = 'http://www.pro-football-reference.com/players/H/HydeCa00.htm'
	resp = requests.get(base)
	page = BeautifulSoup(resp.text)
	tables = get_stats_tables(page)

	path = '/touchdowns'
	path_url = base.replace('.htm', path)
	path_resp = requests.get(path_url)
	path_page = BeautifulSoup(path_resp.text)
	path_tables = get_stats_tables(path_page)


