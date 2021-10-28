import math
import os

from utils import timex, tsv

from cricket_mens_t20_wc_2021 import historical, wc_agenda
from cricket_mens_t20_wc_2021._constants import DIR_DATA
from cricket_mens_t20_wc_2021._utils import log

ODDS_HISTORICAL_FILE = os.path.join(DIR_DATA, 'odds.historical.tsv')
CURRENT_UT = timex.get_unixtime()


def get_p1(odds_index, single_odds_index, team_1, team_2):
    W_ONE_ON_ONE = 8
    W_SINGLE = 4
    W_NOISE = 1

    w_all = 0
    p_all = 0

    p_single = single_odds_index[team_1] / (
        single_odds_index[team_1] + single_odds_index[team_2]
    )
    w_all += W_SINGLE
    p_all += W_SINGLE * p_single

    p_one_on_one = odds_index.get(team_1, {}).get(team_2, None)
    if p_one_on_one is not None:
        w_all += W_ONE_ON_ONE
        p_all += W_ONE_ON_ONE * p_one_on_one

    P_NOISE = 0.5
    w_all += W_NOISE
    p_all += W_NOISE * P_NOISE

    return p_all / w_all


def dedupe(match_list):
    match_index = {}
    for match in match_list:
        match_id = match['date_id'] + match['team_1'] + match['team_2']
        match_index[match_id] = match
    return sorted(match_index.values(), key=lambda match: match['date_id'])


def store_odds_historical():
    match_list1 = historical.load_matches_for_wc_teams()
    match_list2 = wc_agenda.load_agenda()

    match_list = dedupe(match_list1 + match_list2)

    winner_index = {}
    for match in match_list:
        team_1 = match['team_1']
        team_2 = match['team_2']
        if match['winner'] == '':
            continue
        winner = (int)(match['winner'])
        date_id = match['date_id']

        ut = timex.parse_time(date_id, '%Y%m%d')
        d_ut = CURRENT_UT - ut
        d_ut_years = d_ut / timex.SECONDS_IN.YEAR
        HALF_LIFE_IN_YEARS = 1
        w = 1 / math.pow(2, d_ut_years / HALF_LIFE_IN_YEARS)

        if winner == 1:
            team_win = team_1
            team_los = team_2
        elif winner == 2:
            team_win = team_2
            team_los = team_1
        else:
            continue

        if team_win not in winner_index:
            winner_index[team_win] = {}
        if team_los not in winner_index:
            winner_index[team_los] = {}

        if team_los not in winner_index[team_win]:
            winner_index[team_win][team_los] = 0
        if team_win not in winner_index[team_los]:
            winner_index[team_los][team_win] = 0

        winner_index[team_win][team_los] += w

    odds_historical_list = []
    for team_1, team_2_to_n in winner_index.items():
        for team_2, n_1 in team_2_to_n.items():
            n_2 = winner_index[team_2][team_1]
            n_total = n_1 + n_2
            p_1 = (n_1) / (n_total)
            p_2 = 1 - p_1
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
    winner_index = {}
    for d in odds_historical_list:
        team_1 = d['team_1']
        team_2 = d['team_2']
        p_1 = (float)(d['p_1'])
        if team_1 not in winner_index:
            winner_index[team_1] = {}
        winner_index[team_1][team_2] = p_1
    return winner_index


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
    for team_2, p1 in load_odds_historical_index()['AUS'].items():
        print(team_2, p1)
