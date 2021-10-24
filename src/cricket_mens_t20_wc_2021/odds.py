import os
from utils import timex, tsv
from utils.cache import cache
from cricket_mens_t20_wc_2021 import historical
from cricket_mens_t20_wc_2021._constants import CACHE_NAME, CACHE_TIMEOUT, WC_TEAMS, DIR_DATA
from cricket_mens_t20_wc_2021._utils import log

ODDS_HISTORICAL_FILE = os.path.join(DIR_DATA, 'odds.historical.tsv')
def store_odds_historical():
    match_list = historical.load_matches_for_wc_teams()
    result_index = {}
    for match in match_list:
        team_1 = match['team_1']
        team_2 = match['team_2']
        result = (int)(match['result'])

        if result == 1:
            team_win = team_1
            team_los = team_2
        elif result == 2:
            team_win = team_2
            team_los = team_1
        else:
            continue

        if team_win not in result_index:
            result_index[team_win] = {}
        if team_los not in result_index:
            result_index[team_los] = {}

        if team_los not in result_index[team_win]:
            result_index[team_win][team_los] = 0
        if team_win not in result_index[team_los]:
            result_index[team_los][team_win] = 0

        result_index[team_win][team_los] += 1

    odds_historical_list = []
    for team_1, team_2_to_n in result_index.items():
        for team_2, n_1 in team_2_to_n.items():
            n_2 = result_index[team_2][team_1]
            n_total = n_1 + n_2
            p_1 = n_1 / n_total
            p_2 = n_2 / n_total
            odds_historical_list.append({
                'team_1': team_1,
                'team_2': team_2,
                'n_1': n_1,
                'n_2': n_2,
                'n_total': n_total,
                'p_1': p_1,
                'p_2': p_2,
            })
    tsv.write(ODDS_HISTORICAL_FILE, odds_historical_list)
    log.info(f'Wrote odds_historical to {ODDS_HISTORICAL_FILE}')


@cache(CACHE_NAME, CACHE_TIMEOUT)
def load_odds_historical_index():
    odds_historical_list = tsv.read(ODDS_HISTORICAL_FILE)
    result_index = {}
    for d in odds_historical_list:
        team_1 = d['team_1']
        team_2 = d['team_2']
        p_1 = d['p_1']
        if team_1 not in result_index:
            result_index[team_1] = {}
        result_index[team_1][team_2] = p_1
    return result_index

@cache(CACHE_NAME, CACHE_TIMEOUT)
def get_p1(team_1, team_2):
    result_index = load_odds_historical_index()
    return result_index.get(team_1, {}).get(team_2, None)

if __name__ == '__main__':
    print(get_p1('SL', 'IND'))
    print(get_p1('IND', 'SL'))
