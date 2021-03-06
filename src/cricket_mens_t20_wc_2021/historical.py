import os

from bs4 import BeautifulSoup
from utils import timex, tsv, www

from cricket_mens_t20_wc_2021._constants import DIR_DATA, WC_TEAMS
from cricket_mens_t20_wc_2021._utils import log, long_to_short_name

YEAR_LIST = [year for year in range(2012, 2022)]

MATCH_FILE = os.path.join(DIR_DATA, 'matches.all.tsv')


def get_match_file_for_year(year):
    return os.path.join(
        'src/cricket_mens_t20_wc_2021/data',
        f'matches.{year}.tsv',
    )


def parse_cells(cell_values):
    if len(cell_values) != 6:
        return None
    if cell_values[1] == 'Date':
        return None

    ut = timex.parse_time(cell_values[1], '%d/%m/%Y')
    date_id = timex.get_date_id(ut)
    team_1_long, _, team_2_long = cell_values[2].partition(" v. ")
    team_1 = long_to_short_name(team_1_long)
    team_2 = long_to_short_name(team_2_long)

    winner = 0
    if team_1_long in cell_values[4]:
        winner = 1
    elif team_2_long in cell_values[4]:
        winner = 2

    return {
        'date_id': date_id,
        'team_1': team_1,
        'team_2': team_2,
        'winner': winner,
    }


def scrape_matches_for_year(year):
    url = os.path.join(
        'http://www.howstat.com',
        'cricket/Statistics/Matches',
        f'MatchList_T20.asp?Group={year}0101{year}1231&Range={year}',
    )
    html = www.read(url)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')
    match_list = []
    for tr in table.find_all('tr'):
        cell_values = list(
            map(
                lambda td: td.text.strip(),
                tr.find_all('td'),
            )
        )
        match = parse_cells(cell_values)
        if not match:
            continue
        match_list.append(match)
    n_match_list = len(match_list)
    match_file = get_match_file_for_year(year)
    tsv.write(match_file, match_list)
    log.info(f'Scraped {n_match_list} matches for {year} to {match_file}')


def load_matches_for_year(year):
    match_file = get_match_file_for_year(year)
    return tsv.read(match_file)


def scrape_matches(backpopulate=False):
    match_list = []
    for year in YEAR_LIST:
        if year == 2021 or backpopulate:
            scrape_matches_for_year(year)
        match_list += load_matches_for_year(year)

    n_match_list = len(match_list)
    tsv.write(MATCH_FILE, match_list)
    years_str = ','.join(list(map(str, YEAR_LIST)))
    log.info(f'Scraped {n_match_list} matches for {years_str} to {MATCH_FILE}')

    return match_list


def load_matches():
    return tsv.read(MATCH_FILE)


def load_matches_for_wc_teams():
    def is_both_teams_in_wc(match):
        team_1 = match['team_1']
        team_2 = match['team_2']
        return team_1 in WC_TEAMS and team_2 in WC_TEAMS

    match_list = load_matches()
    return list(
        filter(
            is_both_teams_in_wc,
            match_list,
        )
    )
