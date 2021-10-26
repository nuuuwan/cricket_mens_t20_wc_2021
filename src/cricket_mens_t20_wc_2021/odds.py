import math
import os

from utils import timex, tsv

from cricket_mens_t20_wc_2021 import historical
from cricket_mens_t20_wc_2021._constants import DIR_DATA
from cricket_mens_t20_wc_2021._utils import log

ODDS_HISTORICAL_FILE = os.path.join(DIR_DATA, 'odds.historical.tsv')
CURRENT_UT = timex.get_unixtime()


def store_odds_historical():
    match_list = historical.load_matches_for_wc_teams()
    result_index = {}
    for match in match_list:
        team_1 = match['team_1']
        team_2 = match['team_2']
        result = (int)(match['result'])
        date_id = match['date_id']
        ut = timex.parse_time(date_id, '%Y%m%d')
        d_ut = CURRENT_UT - ut
        d_ut_years = d_ut / timex.SECONDS_IN.YEAR
        w = 1 / math.pow(2, d_ut_years)

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

        result_index[team_win][team_los] += w

    odds_historical_list = []
    for team_1, team_2_to_n in result_index.items():
        for team_2, n_1 in team_2_to_n.items():
            n_2 = result_index[team_2][team_1]
            n_total = n_1 + n_2
            p_1 = n_1 / n_total
            p_2 = n_2 / n_total
            odds_historical_list.append(
                {
                    'team_1': team_1,
                    'team_2': team_2,
                    'n_1': n_1,
                    'n_2': n_2,
                    'n_total': n_total,
                    'p_1': p_1,
                    'p_2': p_2,
                }
            )
    tsv.write(ODDS_HISTORICAL_FILE, odds_historical_list)
    log.info(f'Wrote odds_historical to {ODDS_HISTORICAL_FILE}')


def load_odds_historical_index():
    odds_historical_list = tsv.read(ODDS_HISTORICAL_FILE)
    result_index = {}
    for d in odds_historical_list:
        team_1 = d['team_1']
        team_2 = d['team_2']
        p_1 = (float)(d['p_1'])
        if team_1 not in result_index:
            result_index[team_1] = {}
        result_index[team_1][team_2] = p_1
    return result_index


def load_single_odds_historical_index():
    odds_historical_list = tsv.read(ODDS_HISTORICAL_FILE)
    team_to_n_total = {}
    team_to_n_wins = {}
    for d in odds_historical_list:
        team_1 = d['team_1']
        n_total = (float)(d['n_total'])
        n_1 = (float)(d['n_1'])
        if team_1 not in team_to_n_total:
            team_to_n_total[team_1] = 0
            team_to_n_wins[team_1] = 0
        team_to_n_total[team_1] += 1
        team_to_n_wins[team_1] += n_1 / n_total

    single_odds = {}
    for team, n_total in team_to_n_total.items():
        n_1 = team_to_n_wins[team]
        single_odds[team] = n_1 / n_total
    return single_odds


if __name__ == '__main__':
    store_odds_historical()
    for team_2, p1 in load_odds_historical_index()['IND'].items():
        print(team_2, p1)
